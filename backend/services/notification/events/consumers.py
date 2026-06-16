import logging
from backend.shared.events.envelope import EventEnvelope
from backend.services.notification.worker.notification_tasks import process_notification_event
from backend.shared.messaging.rabbitmq import register_consumer_setup, start_consumer

logger = logging.getLogger(__name__)


async def handle_booking_event(envelope: EventEnvelope):
    logger.info(f"[Notification] Received {envelope.event_name}: {envelope.event_id}")
    data = envelope.payload
    passenger_id = data.get("passenger_id") or data.get("user_id")
    if not passenger_id:
        return
    process_notification_event.delay(
        user_id=str(passenger_id),
        event_type=envelope.event_name.value if hasattr(envelope.event_name, 'value') else str(envelope.event_name),
        context={"title": "Booking Update", "message": f"Your booking {data.get('booking_id')} has been updated."},
        event_id=str(envelope.event_id),
        n_type="BOOKING",
    )


async def handle_dispatch_event(envelope: EventEnvelope):
    logger.info(f"[Notification] Received {envelope.event_name}: {envelope.event_id}")
    data = envelope.payload
    passenger_id = data.get("passenger_id") or data.get("user_id")
    if not passenger_id:
        return
    process_notification_event.delay(
        user_id=str(passenger_id),
        event_type=envelope.event_name.value if hasattr(envelope.event_name, 'value') else str(envelope.event_name),
        context={
            "title": "Dispatch Update", 
            "message": f"Driver assigned for booking {data.get('booking_id')}."
        },
        event_id=str(envelope.event_id),
        n_type="DISPATCH",
    )


def init_notification_consumers():
    """Register all notification RabbitMQ consumers."""
    
    async def setup() -> None:
        async def _handle_booking_payload(payload: dict) -> None:
            envelope = EventEnvelope(**payload)
            await handle_booking_event(envelope)

        await start_consumer("notification_booking_queue", ["booking.trip.created", "booking.trip.assigned"], _handle_booking_payload)

        async def _handle_dispatch_payload(payload: dict) -> None:
            envelope = EventEnvelope(**payload)
            await handle_dispatch_event(envelope)

        await start_consumer("notification_dispatch_queue", ["dispatch.driver.selected", "dispatch.assignment.confirmed"], _handle_dispatch_payload)

    register_consumer_setup(setup)
    logger.info("Notification consumers registered.")
