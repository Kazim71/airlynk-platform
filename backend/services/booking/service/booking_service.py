"""
AirLynk — Booking Service.

Implements the Booking state machine, Redis caching, and orchestration.
Integrates with the Pricing Engine for fare calculation.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.booking.events.publishers import BookingEventPublisher
from backend.services.booking.models.booking import Booking, BookingStatus, TripStatus
from backend.services.pricing.schemas.pricing import FareEstimateRequest
from backend.services.pricing.service.pricing_service import PricingService
from backend.services.fleet.repository.fleet_repository import FleetRepository
from backend.shared.exceptions.handlers import ConflictError, NotFoundError
from backend.shared.observability.metrics import BOOKINGS_COMPLETED_TOTAL, BOOKINGS_CREATED_TOTAL

if TYPE_CHECKING:
    from backend.services.booking.repository.booking_repository import BookingRepository
    from backend.services.booking.schemas.booking import AssignDriverRequest, BookingCreate

logger = logging.getLogger(__name__)


class BookingService:
    """Business logic layer for Bookings."""

    def __init__(self, repo: BookingRepository, redis: Redis, db_session: AsyncSession) -> None:  # type: ignore
        self.repo = repo
        self.redis = redis
        self.db_session = db_session
        self.fleet_repo = FleetRepository(db_session)
        self.publisher = BookingEventPublisher()

    async def create_booking(
        self, customer_id: uuid.UUID, data: BookingCreate, correlation_id: uuid.UUID
    ) -> Booking:
        """Create a new booking with pricing from the Pricing Engine."""
        # Use the Pricing Engine to calculate the fare
        estimated_price = await self._calculate_fare(data)

        booking = await self.repo.create_booking(customer_id, data, estimated_price)

        # Cache active booking in Redis
        cache_key = f"active_booking:{booking.id}"
        await self.redis.setex(cache_key, 3600, str(booking.booking_status))

        await self.publisher.publish_booking_created(booking.id, customer_id, correlation_id)
        BOOKINGS_CREATED_TOTAL.inc()
        logger.info(f"Booking {booking.id} created by customer {customer_id} | fare=₹{estimated_price}")
        return booking

    async def _calculate_fare(self, data: BookingCreate) -> float:
        """Delegate fare calculation to the Pricing Engine.

        Determines city from the pickup location string and uses the geo
        coordinates for distance/duration estimation.
        """
        try:
            # Extract city from pickup_location (format: "City - Airport Name")
            city = data.pickup_location.split(" - ")[0].strip() if " - " in data.pickup_location else data.pickup_location.strip()

            # Use Haversine-based distance estimate (same as geo service)
            from backend.services.geo.schemas.geo import RouteRequest
            from backend.services.geo.service.geo_service import GeoService
            geo_svc = GeoService()
            geo_result = await geo_svc.estimate_route(RouteRequest(
                pickup_lat=data.pickup_lat,
                pickup_lng=data.pickup_lng,
                dropoff_lat=data.dropoff_lat,
                dropoff_lng=data.dropoff_lng,
            ))
            distance_km = Decimal(str(geo_result.distance_km))
            duration_mins = geo_result.duration_minutes

            # Call pricing engine
            pricing_svc = PricingService(self.db_session)
            fare_request = FareEstimateRequest(
                pickup_lat=data.pickup_lat,
                pickup_lng=data.pickup_lng,
                dropoff_lat=data.dropoff_lat,
                dropoff_lng=data.dropoff_lng,
                city=city,
                vehicle_type="sedan",  # Default; can be extended with BookingCreate field
                estimated_duration_minutes=max(duration_mins, 1),
                estimated_distance_km=max(distance_km, Decimal("0.1")),
                is_airport=True,  # AirLynk is an airport transfer service
            )
            fare_response = await pricing_svc.calculate_fare(fare_request)
            return float(fare_response.total_estimate)

        except Exception as e:
            # If pricing fails (no rules, etc.), use a safe fallback
            logger.warning(f"Pricing engine failed, using fallback: {e}")
            return 500.00  # Safe minimum fallback for airport transfers

    async def assign_driver(
        self,
        booking_id: uuid.UUID,
        data: AssignDriverRequest,
        operator_id: uuid.UUID,
        correlation_id: uuid.UUID,
    ) -> Booking:
        """Assign driver to booking using Redis distributed lock."""
        lock_key = f"lock:booking_assign:{booking_id}"

        # Distributed lock to prevent race conditions during assignment
        lock_acquired = await self.redis.set(lock_key, "locked", nx=True, ex=10)
        if not lock_acquired:
            raise ConflictError("Booking is currently being modified by another process")

        try:
            booking = await self.repo.get_booking_by_id(booking_id)
            if not booking:
                raise NotFoundError("Booking not found")

            # State Machine validation
            if booking.booking_status not in [BookingStatus.CREATED, BookingStatus.CONFIRMED, BookingStatus.PAYMENT_AUTHORIZED, BookingStatus.DISPATCHING]:
                raise ConflictError(
                    f"Cannot assign driver to booking in state: {booking.booking_status}"
                )

            booking = await self.repo.assign_driver(
                booking, data.driver_id, data.vehicle_id, operator_id
            )

            await self.redis.setex(
                f"active_booking:{booking.id}", 3600, str(booking.booking_status)
            )
            await self.publisher.publish_driver_assigned(
                booking.id, data.driver_id, data.vehicle_id, correlation_id
            )
            logger.info(f"Driver {data.driver_id} assigned to booking {booking.id}")
            return booking
        finally:
            await self.redis.delete(lock_key)

    async def start_trip(
        self, booking_id: uuid.UUID, user_id: uuid.UUID, correlation_id: uuid.UUID
    ) -> Booking:
        """Start the trip for a booking."""
        booking = await self.repo.get_booking_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")

        # Resolve Fleet Driver from User ID
        fleet_driver = await self.fleet_repo.get_driver_by_user_id(user_id)
        driver_id = fleet_driver.id if fleet_driver else user_id

        if booking.assigned_driver_id != driver_id:
            raise ConflictError("Driver is not assigned to this booking")

        if booking.booking_status != BookingStatus.DRIVER_ASSIGNED:
            raise ConflictError(f"Cannot start trip from state: {booking.booking_status}")

        booking = await self.repo.update_booking_status(
            booking, BookingStatus.IN_PROGRESS, driver_id
        )
        await self.repo.update_trip_status(
            booking.trip, TripStatus.STARTED, started_at=datetime.now(UTC)
        )

        await self.redis.setex(f"active_booking:{booking.id}", 3600, str(booking.booking_status))
        await self.publisher.publish_trip_started(booking.id, booking.trip.id, correlation_id)
        logger.info(f"Trip started for booking {booking.id}")
        return booking

    async def complete_trip(
        self, booking_id: uuid.UUID, user_id: uuid.UUID, correlation_id: uuid.UUID
    ) -> Booking:
        """Complete the trip for a booking."""
        booking = await self.repo.get_booking_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")

        # Resolve Fleet Driver from User ID
        fleet_driver = await self.fleet_repo.get_driver_by_user_id(user_id)
        driver_id = fleet_driver.id if fleet_driver else user_id

        if booking.assigned_driver_id != driver_id:
            raise ConflictError("Driver is not assigned to this booking")

        if booking.booking_status != BookingStatus.IN_PROGRESS:
            raise ConflictError(f"Cannot complete trip from state: {booking.booking_status}")

        booking = await self.repo.update_booking_status(
            booking, BookingStatus.COMPLETED, driver_id
        )
        await self.repo.update_trip_status(
            booking.trip, TripStatus.COMPLETED, completed_at=datetime.now(UTC)
        )

        await self.redis.delete(f"active_booking:{booking.id}")
        await self.publisher.publish_trip_completed(booking.id, booking.trip.id, correlation_id)
        BOOKINGS_COMPLETED_TOTAL.inc()
        logger.info(f"Trip completed for booking {booking.id}")
        return booking

    async def cancel_booking(
        self, booking_id: uuid.UUID, user_id: uuid.UUID, correlation_id: uuid.UUID
    ) -> Booking:
        """Cancel a booking."""
        booking = await self.repo.get_booking_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")

        if booking.booking_status in [
            BookingStatus.COMPLETED,
            BookingStatus.CANCELLED,
            BookingStatus.FAILED,
        ]:
            raise ConflictError(f"Cannot cancel booking in state: {booking.booking_status}")

        booking = await self.repo.update_booking_status(booking, BookingStatus.CANCELLED, user_id)
        if booking.trip:
            await self.repo.update_trip_status(booking.trip, TripStatus.CANCELLED)

        await self.redis.delete(f"active_booking:{booking.id}")
        await self.publisher.publish_booking_cancelled(booking.id, user_id, correlation_id)
        logger.info(f"Booking {booking.id} cancelled by {user_id}")
        return booking

    async def authorize_payment(self, booking_id: uuid.UUID) -> Booking:
        """Handle payment authorization success."""
        booking = await self.repo.get_booking_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        
        if booking.booking_status in [BookingStatus.CREATED, BookingStatus.CONFIRMED]:
            booking = await self.repo.update_booking_status(booking, BookingStatus.PAYMENT_AUTHORIZED, booking.customer_id)
            await self.redis.setex(f"active_booking:{booking.id}", 3600, str(booking.booking_status))
            logger.info(f"Payment authorized for booking {booking.id}")
            
            # Auto-transition to dispatching
            booking = await self.repo.update_booking_status(booking, BookingStatus.DISPATCHING, booking.customer_id)
            await self.redis.setex(f"active_booking:{booking.id}", 3600, str(booking.booking_status))
        return booking

    async def get_booking(self, booking_id: uuid.UUID) -> Booking:
        booking = await self.repo.get_booking_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")
        return booking

    async def get_customer_bookings(self, customer_id: uuid.UUID) -> list[Booking]:
        bookings = await self.repo.list_customer_bookings(customer_id)
        return list(bookings)

    async def get_all_bookings(self) -> list[Booking]:
        bookings = await self.repo.list_all_bookings()
        return list(bookings)
