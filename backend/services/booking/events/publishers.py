"""
AirLynk — Booking Event Publishers.
"""

from __future__ import annotations

import uuid

from backend.shared.events.envelope import EventEnvelope, EventName
from backend.shared.messaging.rabbitmq import publish_event


class BookingEventPublisher:
    """Handles publishing domain events for bookings."""

    @staticmethod
    async def publish_booking_created(
        booking_id: uuid.UUID, customer_id: uuid.UUID, correlation_id: uuid.UUID
    ) -> None:
        envelope = EventEnvelope(
            event_name=EventName.BOOKING_TRIP_CREATED,
            producer="booking-service",
            correlation_id=correlation_id,
            payload={"booking_id": str(booking_id), "customer_id": str(customer_id)},
        )
        await publish_event(envelope.event_name, envelope.model_dump())

    @staticmethod
    async def publish_driver_assigned(
        booking_id: uuid.UUID,
        driver_id: uuid.UUID,
        vehicle_id: uuid.UUID,
        correlation_id: uuid.UUID,
    ) -> None:
        envelope = EventEnvelope(
            event_name=EventName.BOOKING_TRIP_ASSIGNED,
            producer="booking-service",
            correlation_id=correlation_id,
            payload={
                "booking_id": str(booking_id),
                "driver_id": str(driver_id),
                "vehicle_id": str(vehicle_id),
            },
        )
        await publish_event(envelope.event_name, envelope.model_dump())

    @staticmethod
    async def publish_trip_started(
        booking_id: uuid.UUID, trip_id: uuid.UUID, correlation_id: uuid.UUID
    ) -> None:
        envelope = EventEnvelope(
            event_name="booking.trip.started",  # Extending EventName dynamically for this example
            producer="booking-service",
            correlation_id=correlation_id,
            payload={"booking_id": str(booking_id), "trip_id": str(trip_id)},
        )
        await publish_event(envelope.event_name, envelope.model_dump())

    @staticmethod
    async def publish_trip_completed(
        booking_id: uuid.UUID, trip_id: uuid.UUID, correlation_id: uuid.UUID
    ) -> None:
        envelope = EventEnvelope(
            event_name=EventName.BOOKING_TRIP_COMPLETED,
            producer="booking-service",
            correlation_id=correlation_id,
            payload={"booking_id": str(booking_id), "trip_id": str(trip_id)},
        )
        await publish_event(envelope.event_name, envelope.model_dump())

    @staticmethod
    async def publish_booking_cancelled(
        booking_id: uuid.UUID, cancelled_by: uuid.UUID, correlation_id: uuid.UUID
    ) -> None:
        envelope = EventEnvelope(
            event_name="booking.trip.cancelled",
            producer="booking-service",
            correlation_id=correlation_id,
            payload={"booking_id": str(booking_id), "cancelled_by": str(cancelled_by)},
        )
        await publish_event(envelope.event_name, envelope.model_dump())
