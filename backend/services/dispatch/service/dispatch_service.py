"""
AirLynk — Dispatch Orchestration Service.

Coordinates finding drivers, handling timeouts, locking concurrency,
and publishing domain events.
"""

import json
import logging
from uuid import UUID

from redis.asyncio import Redis

from backend.services.booking.repository.booking_repository import BookingRepository
from backend.services.dispatch.events.publishers import (
    publish_assignment_confirmed,
    publish_assignment_failed,
    publish_dispatch_requested,
    publish_driver_selected,
    publish_retry_triggered,
)
from backend.services.dispatch.models.dispatch import AttemptStatus, DispatchStatus
from backend.services.dispatch.repository.dispatch_repository import DispatchRepository
from backend.services.dispatch.service.matching_engine import MatchingEngine
from backend.services.fleet.repository.fleet_repository import FleetRepository
from backend.shared.exceptions.handlers import ValidationError

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
OFFER_TIMEOUT_SECONDS = 30


class DispatchService:
    def __init__(
        self,
        dispatch_repo: DispatchRepository,
        booking_repo: BookingRepository,
        fleet_repo: FleetRepository,
        redis_client: Redis,
    ) -> None:
        self.dispatch_repo = dispatch_repo
        self.booking_repo = booking_repo
        self.fleet_repo = fleet_repo
        self.redis = redis_client
        self.engine = MatchingEngine()

    async def update_driver_availability(
        self, driver_id: UUID, is_available: bool, lat: float | None, lon: float | None
    ) -> None:
        """Update driver status in Redis and Fleet DB."""
        driver = await self.fleet_repo.get_driver_by_id(driver_id)
        if not driver:
            raise ValidationError("Driver not found")

        # In a real app, update driver status in Postgres via Fleet domain API/service.
        # For simplicity, we directly write to Redis active pool.
        redis_key = f"dispatch:driver:availability:{driver_id}"
        
        if is_available:
            payload = {
                "driver_id": str(driver_id),
                "latitude": lat or 0.0,
                "longitude": lon or 0.0,
            }
            await self.redis.set(redis_key, json.dumps(payload))
            logger.info(f"Driver {driver_id} is now ONLINE.")
        else:
            await self.redis.delete(redis_key)
            logger.info(f"Driver {driver_id} is now OFFLINE.")

    async def start_dispatch(self, booking_id: UUID) -> None:
        """Entry point to start the dispatch process for a booking."""
        booking = await self.booking_repo.get_booking_by_id(booking_id)
        if not booking:
            logger.error(f"Cannot dispatch for unknown booking {booking_id}")
            return

        # 1. Create or get existing DispatchRequest
        req = await self.dispatch_repo.get_dispatch_request_by_booking(booking_id)
        if not req:
            req = await self.dispatch_repo.create_dispatch_request(booking_id)

        if req.status in [DispatchStatus.ASSIGNED, DispatchStatus.FAILED]:
            logger.info(f"Dispatch {req.id} is already in terminal state {req.status}")
            return

        if req.retry_count >= MAX_RETRIES:
            await self.dispatch_repo.update_dispatch_status(req.id, DispatchStatus.FAILED)
            await publish_assignment_failed(booking_id, "Max retries exceeded")
            logger.warning(f"Booking {booking_id} dispatch failed: max retries.")
            return

        # Use Redis lock to prevent concurrent dispatch loops for the same booking
        lock_key = f"lock:dispatch:{booking_id}"
        lock_acquired = await self.redis.set(lock_key, "locked", nx=True, ex=10)
        if not lock_acquired:
            logger.warning(f"Dispatch for {booking_id} is already in progress.")
            return

        try:
            await self.dispatch_repo.update_dispatch_status(req.id, DispatchStatus.ASSIGNING)
            await publish_dispatch_requested(booking_id, req.retry_count)

            # 2. Get active drivers from Redis
            driver_keys = await self.redis.keys("dispatch:driver:availability:*")
            active_drivers = []
            for k in driver_keys:
                data = await self.redis.get(k)
                if data:
                    active_drivers.append(json.loads(data))

            if not active_drivers:
                # No drivers available -> increment retry and queue for later
                logger.info(f"No active drivers for {booking_id}, will retry.")
                await self.dispatch_repo.update_dispatch_status(req.id, DispatchStatus.PENDING, increment_retry=True)
                await publish_retry_triggered(booking_id, req.retry_count + 1)
                return

            # 3. Match and score drivers. (Mock pickup coords for now)
            pickup_lat = 0.0
            pickup_lon = 0.0
            scored = self.engine.score_drivers(booking, active_drivers, pickup_lat, pickup_lon)

            # Select highest scoring driver that hasn't been pinged yet
            pinged_driver_ids = {a.driver_id for a in req.attempts}
            selected_driver = None
            for s in scored:
                if s.driver_id not in pinged_driver_ids:
                    selected_driver = s
                    break

            if not selected_driver:
                logger.info(f"All active drivers already pinged for {booking_id}.")
                await self.dispatch_repo.update_dispatch_status(req.id, DispatchStatus.FAILED)
                await publish_assignment_failed(booking_id, "Exhausted all available drivers")
                return

            # 4. Record the attempt
            attempt = await self.dispatch_repo.create_dispatch_attempt(req.id, selected_driver.driver_id)
            
            # Set a timeout in Redis for this specific attempt
            attempt_ttl_key = f"dispatch:attempt:{attempt.id}:timeout"
            await self.redis.set(attempt_ttl_key, str(booking_id), ex=OFFER_TIMEOUT_SECONDS)

            await publish_driver_selected(booking_id, attempt.id, selected_driver.driver_id)
            logger.info(f"Driver {selected_driver.driver_id} selected for booking {booking_id}. Attempt: {attempt.id}")

        finally:
            await self.redis.delete(lock_key)

    async def handle_driver_decision(self, attempt_id: UUID, accepted: bool) -> None:
        """Process a driver's explicit accept or reject."""
        # Clean up timeout key
        await self.redis.delete(f"dispatch:attempt:{attempt_id}:timeout")

        status = AttemptStatus.ACCEPTED if accepted else AttemptStatus.REJECTED
        attempt = await self.dispatch_repo.update_attempt_status(attempt_id, status)
        
        if not attempt:
            raise ValidationError("Dispatch attempt not found")
            
        req = await self.dispatch_repo.get_dispatch_request(attempt.dispatch_request_id)
        if not req:
            raise ValidationError("Dispatch request not found")

        if accepted:
            # Complete the workflow
            await self.dispatch_repo.update_dispatch_status(req.id, DispatchStatus.ASSIGNED)
            await publish_assignment_confirmed(req.booking_id, attempt.driver_id)
            logger.info(f"Driver {attempt.driver_id} ACCEPTED booking {req.booking_id}")
        else:
            logger.info(f"Driver {attempt.driver_id} REJECTED booking {req.booking_id}")
            # Retry loop
            await self.dispatch_repo.update_dispatch_status(req.id, DispatchStatus.PENDING, increment_retry=True)
            await self.start_dispatch(req.booking_id)
