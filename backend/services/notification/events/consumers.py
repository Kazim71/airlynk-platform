"""
AirLynk — Notification Event Consumers.
"""

import logging

from backend.services.notification.worker import process_notification_event
from backend.shared.events.envelope import EventEnvelope, EventName

logger = logging.getLogger(__name__)


def init_notification_consumers() -> None:
    """Register RabbitMQ consumers for notification domain."""
    from backend.shared.messaging.rabbitmq import register_consumer_setup, start_consumer

    async def setup() -> None:
        # Route these events to the notification worker
        notification_keys = [
            EventName.AUTH_USER_REGISTERED,
            EventName.BOOKING_TRIP_CREATED,
            EventName.BOOKING_TRIP_ASSIGNED,
            EventName.BOOKING_TRIP_COMPLETED,
            EventName.DISPATCH_DRIVER_SELECTED,
            EventName.DISPATCH_ASSIGNMENT_FAILED,
        ]

        async def _handle_notification_payload(payload: dict) -> None:  # type: ignore
            envelope = EventEnvelope(**payload)
            # Send to Celery to process asynchronously
            process_notification_event.delay(
                event_name=envelope.event_name,
                payload=envelope.payload,
                event_id=str(envelope.event_id),
            )

        await start_consumer("notification_events_queue", notification_keys, _handle_notification_payload)  # type: ignore

    register_consumer_setup(setup)
