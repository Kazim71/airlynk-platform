"""
AirLynk — Dispatch Event Publishers.
"""

from uuid import UUID

from backend.shared.events.envelope import EventEnvelope, EventName
from backend.shared.messaging.rabbitmq import publish_event


async def publish_dispatch_requested(booking_id: UUID, retry_count: int) -> None:
    """Publish that a dispatch loop has been requested for a booking."""
    event = EventEnvelope.create(
        event_name=EventName.DISPATCH_ASSIGNMENT_REQUESTED,
        payload={"booking_id": str(booking_id), "retry_count": retry_count},
    )
    await publish_event("dispatch.assignment.requested", event.model_dump())


async def publish_driver_selected(
    booking_id: UUID, attempt_id: UUID, driver_id: UUID
) -> None:
    """Publish that a specific driver was selected and offered the ride."""
    event = EventEnvelope.create(
        event_name=EventName.DISPATCH_DRIVER_SELECTED,
        payload={
            "booking_id": str(booking_id),
            "attempt_id": str(attempt_id),
            "driver_id": str(driver_id),
        },
    )
    await publish_event("dispatch.driver.selected", event.model_dump())


async def publish_assignment_confirmed(booking_id: UUID, driver_id: UUID) -> None:
    """Publish that the driver accepted and assignment is confirmed."""
    event = EventEnvelope.create(
        event_name=EventName.DISPATCH_ASSIGNMENT_CONFIRMED,
        payload={"booking_id": str(booking_id), "driver_id": str(driver_id)},
    )
    await publish_event("dispatch.assignment.confirmed", event.model_dump())


async def publish_assignment_failed(booking_id: UUID, reason: str) -> None:
    """Publish that dispatch completely failed (e.g., max retries reached)."""
    event = EventEnvelope.create(
        event_name=EventName.DISPATCH_ASSIGNMENT_FAILED,
        payload={"booking_id": str(booking_id), "reason": reason},
    )
    await publish_event("dispatch.assignment.failed", event.model_dump())


async def publish_retry_triggered(booking_id: UUID, attempt_number: int) -> None:
    """Publish that a dispatch retry was triggered."""
    event = EventEnvelope.create(
        event_name=EventName.DISPATCH_RETRY_TRIGGERED,
        payload={"booking_id": str(booking_id), "attempt_number": attempt_number},
    )
    await publish_event("dispatch.retry.triggered", event.model_dump())
