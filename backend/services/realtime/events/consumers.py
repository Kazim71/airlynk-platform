"""
AirLynk — Realtime Event Consumers.
"""

import logging

from backend.services.realtime.schemas.tracking import RealtimeEvent
from backend.services.realtime.service.tracking_service import (
    CHANNEL_BOOKING_PREFIX,
    CHANNEL_DRIVER_PREFIX,
    CHANNEL_OPERATORS,
)
from backend.services.realtime.websocket.manager import manager
from backend.shared.events.envelope import EventEnvelope, EventName

logger = logging.getLogger(__name__)


async def handle_booking_event(envelope: EventEnvelope) -> None:
    """Handle booking events and broadcast to booking and operator channels."""
    booking_id = envelope.payload.get("booking_id")
    if not booking_id:
        return

    rt_event = RealtimeEvent(
        event=envelope.event_name, data=envelope.payload, timestamp=envelope.timestamp
    )
    event_json = rt_event.model_dump_json()

    # Broadcast to specific booking channel
    await manager.broadcast_to_channel(f"{CHANNEL_BOOKING_PREFIX}{booking_id}", event_json)
    # Broadcast to operators
    await manager.broadcast_to_channel(CHANNEL_OPERATORS, event_json)


async def handle_dispatch_event(envelope: EventEnvelope) -> None:
    """Handle dispatch events and broadcast to driver, booking, and operator channels."""
    booking_id = envelope.payload.get("booking_id")
    driver_id = envelope.payload.get("driver_id")

    rt_event = RealtimeEvent(
        event=envelope.event_name, data=envelope.payload, timestamp=envelope.timestamp
    )
    event_json = rt_event.model_dump_json()

    # Broadcast to operators
    await manager.broadcast_to_channel(CHANNEL_OPERATORS, event_json)

    # Broadcast to specific booking channel if applicable
    if booking_id:
        await manager.broadcast_to_channel(f"{CHANNEL_BOOKING_PREFIX}{booking_id}", event_json)

    # Broadcast to specific driver channel if applicable
    if driver_id:
        await manager.broadcast_to_channel(f"{CHANNEL_DRIVER_PREFIX}{driver_id}", event_json)


def init_realtime_consumers() -> None:
    """Register RabbitMQ consumers for realtime domain."""
    from backend.shared.messaging.rabbitmq import register_consumer_setup, start_consumer

    async def setup() -> None:
        # Route booking events
        booking_keys = [
            EventName.BOOKING_TRIP_CREATED,
            EventName.BOOKING_TRIP_ASSIGNED,
            EventName.BOOKING_TRIP_STARTED,
            EventName.BOOKING_TRIP_COMPLETED,
            EventName.BOOKING_TRIP_CANCELLED,
        ]

        async def _handle_booking_payload(payload: dict) -> None:  # type: ignore
            envelope = EventEnvelope(**payload)
            await handle_booking_event(envelope)

        await start_consumer("realtime_booking_queue", booking_keys, _handle_booking_payload)  # type: ignore

        # Route dispatch events
        dispatch_keys = [
            EventName.DISPATCH_ASSIGNMENT_REQUESTED,
            EventName.DISPATCH_DRIVER_SELECTED,
            EventName.DISPATCH_ASSIGNMENT_CONFIRMED,
            EventName.DISPATCH_ASSIGNMENT_FAILED,
            EventName.DISPATCH_RETRY_TRIGGERED,
        ]

        async def _handle_dispatch_payload(payload: dict) -> None:  # type: ignore
            envelope = EventEnvelope(**payload)
            await handle_dispatch_event(envelope)

        await start_consumer("realtime_dispatch_queue", dispatch_keys, _handle_dispatch_payload)  # type: ignore

    register_consumer_setup(setup)
