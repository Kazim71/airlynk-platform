"""
AirLynk — Dispatch Event Consumers.
"""

import logging
from uuid import UUID

from backend.services.booking.repository.booking_repository import BookingRepository
from backend.services.dispatch.repository.dispatch_repository import DispatchRepository
from backend.services.dispatch.service.dispatch_service import DispatchService
from backend.services.fleet.repository.fleet_repository import FleetRepository
from backend.shared.database.session import get_db_session
from backend.shared.events.envelope import EventEnvelope, EventName
from backend.shared.cache.redis_client import get_redis

logger = logging.getLogger(__name__)


async def handle_booking_created(event: EventEnvelope) -> None:
    """Triggered when a new booking is created and needs a driver."""
    booking_id_str = event.payload.get("booking_id")
    if not booking_id_str:
        return

    booking_id = UUID(booking_id_str)
    logger.info(f"Dispatch received booking_created for {booking_id}")

    # Use scoped session
    async for session in get_db_session():
        redis = get_redis()
        dispatch_repo = DispatchRepository(session)
        booking_repo = BookingRepository(session)
        fleet_repo = FleetRepository(session)
        
        service = DispatchService(dispatch_repo, booking_repo, fleet_repo, redis)
        await service.start_dispatch(booking_id)


def get_dispatch_consumers() -> dict:
    """Return the map of events to handlers for the dispatch domain."""
    return {
        EventName.BOOKING_TRIP_CREATED: handle_booking_created,
    }
