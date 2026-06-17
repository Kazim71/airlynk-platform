"""
AirLynk — Booking Event Consumers.
"""
import logging
import uuid
from backend.shared.messaging.rabbitmq import start_consumer, register_consumer_setup
from backend.shared.database.session import get_db_session
from backend.services.booking.service.booking_service import BookingService
from backend.services.booking.repository.booking_repository import BookingRepository
from backend.shared.cache.redis_client import get_redis

logger = logging.getLogger(__name__)

async def handle_payment_status(message: dict) -> None:
    intent_id = message.get("intent_id")
    booking_id = message.get("booking_id")
    status = message.get("status")
    
    if status == "authorized":
        async for session in get_db_session():
            repo = BookingRepository(session)
            redis = get_redis()
            service = BookingService(repo, redis)
            try:
                await service.authorize_payment(uuid.UUID(booking_id))
            except Exception as e:
                logger.error(f"Failed to authorize payment for booking {booking_id}: {e}")

def init_booking_consumers() -> None:
    async def setup_consumer() -> None:
        await start_consumer(
            queue_name="booking_payment_queue",
            routing_keys=["payment.status.updated"],
            callback=handle_payment_status
        )
    register_consumer_setup(setup_consumer)
    logger.info("Booking event consumers registered")
