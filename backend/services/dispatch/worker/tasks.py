"""
AirLynk — Dispatch Celery Workers.

Handles asynchronous timeout checking and escalations.
"""

import asyncio
import logging
from uuid import UUID

from asgiref.sync import async_to_sync

from backend.services.booking.repository.booking_repository import BookingRepository
from backend.services.dispatch.models.dispatch import AttemptStatus
from backend.services.dispatch.repository.dispatch_repository import DispatchRepository
from backend.services.dispatch.service.dispatch_service import DispatchService
from backend.services.fleet.repository.fleet_repository import FleetRepository
from backend.shared.database.session import get_db_session
from backend.shared.cache.redis_client import get_redis
from backend.worker.celery_app import celery_app

logger = logging.getLogger(__name__)


async def _process_dispatch_timeout(attempt_id: UUID) -> None:
    async for session in get_db_session():
        redis = get_redis()
        dispatch_repo = DispatchRepository(session)
        booking_repo = BookingRepository(session)
        fleet_repo = FleetRepository(session)

        # Check attempt status
        attempt = await dispatch_repo.update_attempt_status(attempt_id, AttemptStatus.TIMEOUT)
        if not attempt:
            return

        # It means it timed out. Let's restart the dispatch logic.
        logger.warning(f"Dispatch Attempt {attempt_id} timed out. Retrying dispatch...")
        
        # We must increment retry and re-dispatch. 
        # Using handle_driver_decision with accepted=False is semantically similar but it marks it as REJECTED.
        # We explicitly set TIMEOUT above, so let's just trigger a new dispatch.
        req = await dispatch_repo.get_dispatch_request(attempt.dispatch_request_id)
        if req:
            service = DispatchService(dispatch_repo, booking_repo, fleet_repo, redis)
            await service.handle_driver_decision(attempt_id, accepted=False)


@celery_app.task(name="dispatch.handle_attempt_timeout") # type: ignore
def handle_attempt_timeout(attempt_id_str: str) -> None:
    """Fired after N seconds to check if a driver accepted the offer."""
    attempt_id = UUID(attempt_id_str)
    
    # Run async logic synchronously inside Celery
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Fallback if somehow running in event loop thread
        asyncio.ensure_future(_process_dispatch_timeout(attempt_id))
    else:
        loop.run_until_complete(_process_dispatch_timeout(attempt_id))
