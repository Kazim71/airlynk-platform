"""
Tests for backend.shared.events.envelope — EventEnvelope serialisation.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from backend.shared.events.envelope import EventEnvelope, EventName


class TestEventEnvelope:
    """Verify event envelope model behaviour."""

    def test_create_envelope_with_defaults(self) -> None:
        envelope = EventEnvelope(
            event_name=EventName.AUTH_USER_LOGIN_SUCCESS,
            producer="auth-service",
        )
        assert envelope.event_name == "auth.user.login_success"
        assert envelope.event_version == "1.0"
        assert envelope.producer == "auth-service"
        assert isinstance(envelope.event_id, uuid.UUID)
        assert isinstance(envelope.correlation_id, uuid.UUID)
        assert isinstance(envelope.timestamp, datetime)
        assert envelope.payload == {}

    def test_create_envelope_with_payload(self) -> None:
        payload = {"user_id": "abc-123", "ip_address": "10.0.0.1"}
        envelope = EventEnvelope(
            event_name=EventName.AUTH_USER_LOGIN_FAILED,
            producer="auth-service",
            payload=payload,
        )
        assert envelope.payload == payload

    def test_envelope_json_serialisation(self) -> None:
        envelope = EventEnvelope(
            event_name="booking.trip.created",
            producer="booking-service",
            payload={"booking_id": "xyz"},
        )
        json_str = envelope.model_dump_json()
        assert "booking.trip.created" in json_str
        assert "booking-service" in json_str

    def test_envelope_roundtrip(self) -> None:
        original = EventEnvelope(
            event_name=EventName.NOTIFICATION_EMAIL_SENT,
            producer="notification-service",
            payload={"recipient": "user@example.com"},
        )
        data = original.model_dump(mode="json")
        restored = EventEnvelope.model_validate(data)
        assert restored.event_name == original.event_name
        assert restored.producer == original.producer


class TestEventNameConstants:
    """Verify all event name constants match the documented format."""

    def test_event_names_follow_convention(self) -> None:
        for event in EventName:
            parts = event.value.split(".")
            assert len(parts) >= 3, f"Event '{event}' doesn't follow service.domain.action format"

    def test_auth_events_exist(self) -> None:
        assert EventName.AUTH_USER_REGISTERED.value == "auth.user.registered"
        assert EventName.AUTH_USER_LOGIN_SUCCESS.value == "auth.user.login_success"
        assert EventName.AUTH_USER_LOGIN_FAILED.value == "auth.user.login_failed"
        assert EventName.AUTH_TOKEN_REFRESHED.value == "auth.token.refreshed"

    def test_booking_events_exist(self) -> None:
        assert EventName.BOOKING_TRIP_CREATED.value == "booking.trip.created"
        assert EventName.BOOKING_TRIP_ASSIGNED.value == "booking.trip.assigned"
        assert EventName.BOOKING_TRIP_COMPLETED.value == "booking.trip.completed"
