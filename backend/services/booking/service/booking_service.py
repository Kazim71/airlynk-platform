"""
AirLynk — Booking Service.

Implements the Booking state machine, Redis caching, and orchestration.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from redis.asyncio import Redis

from backend.services.booking.events.publishers import BookingEventPublisher
from backend.services.booking.models.booking import Booking, BookingStatus, TripStatus
from backend.services.booking.repository.booking_repository import BookingRepository
from backend.services.booking.schemas.booking import AssignDriverRequest, BookingCreate
from backend.shared.exceptions.handlers import ConflictError, NotFoundError

logger = logging.getLogger(__name__)


class BookingService:
    """Business logic layer for Bookings."""

    def __init__(self, repo: BookingRepository, redis: Redis) -> None:  # type: ignore
        self.repo = repo
        self.redis = redis
        self.publisher = BookingEventPublisher()

    async def create_booking(
        self, customer_id: uuid.UUID, data: BookingCreate, correlation_id: uuid.UUID
    ) -> Booking:
        """Create a new booking."""
        # Domain logic: Calculate price (mocked)
        estimated_price = 45.00 * data.passenger_count

        booking = await self.repo.create_booking(customer_id, data, estimated_price)

        # Cache active booking in Redis
        cache_key = f"active_booking:{booking.id}"
        await self.redis.setex(cache_key, 3600, str(booking.booking_status))

        await self.publisher.publish_booking_created(booking.id, customer_id, correlation_id)
        logger.info(f"Booking {booking.id} created by customer {customer_id}")
        return booking

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
            if booking.booking_status not in [BookingStatus.CREATED, BookingStatus.CONFIRMED]:
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
        self, booking_id: uuid.UUID, driver_id: uuid.UUID, correlation_id: uuid.UUID
    ) -> Booking:
        """Start the trip for a booking."""
        booking = await self.repo.get_booking_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")

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
        self, booking_id: uuid.UUID, driver_id: uuid.UUID, correlation_id: uuid.UUID
    ) -> Booking:
        """Complete the trip for a booking."""
        booking = await self.repo.get_booking_by_id(booking_id)
        if not booking:
            raise NotFoundError("Booking not found")

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
