"""
AirLynk — Event Envelope model and domain event constants.

Every event published to RabbitMQ MUST be wrapped in an ``EventEnvelope`` so
that consumers have a consistent contract.  See EVENT_CATALOG.md §Event
Envelope Structure.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Event Name Constants — EVENT_CATALOG.md
# ---------------------------------------------------------------------------


class EventName(StrEnum):
    """Canonical event names following ``service.domain.action`` convention."""

    # Authentication events
    AUTH_USER_REGISTERED = "auth.user.registered"
    AUTH_USER_LOGIN_SUCCESS = "auth.user.login_success"
    AUTH_USER_LOGIN_FAILED = "auth.user.login_failed"
    AUTH_TOKEN_REFRESHED = "auth.token.refreshed"

    # Booking events
    BOOKING_TRIP_CREATED = "booking.trip.created"
    BOOKING_TRIP_ASSIGNED = "booking.trip.assigned"
    BOOKING_TRIP_COMPLETED = "booking.trip.completed"

    # Notification events
    NOTIFICATION_EMAIL_SENT = "notification.email.sent"
    NOTIFICATION_EMAIL_FAILED = "notification.email.failed"

    # Security events
    SECURITY_SUSPICIOUS_ACTIVITY = "security.suspicious_activity.detected"
    SECURITY_RATE_LIMIT_TRIGGERED = "security.rate_limit.triggered"

    # Operational events
    SYSTEM_HEALTH_DEGRADED = "system.health.degraded"
    SYSTEM_QUEUE_BACKLOG = "system.queue.backlog_detected"


# ---------------------------------------------------------------------------
# Event Envelope — the wire format for all domain events
# ---------------------------------------------------------------------------


class EventEnvelope(BaseModel):
    """Standard envelope wrapping every domain event.

    Matches the JSON schema defined in EVENT_CATALOG.md::

        {
          "event_id": "uuid",
          "event_name": "auth.user.login_success",
          "event_version": "1.0",
          "timestamp": "2026-06-14T10:00:00Z",
          "producer": "auth-service",
          "correlation_id": "uuid",
          "payload": {}
        }
    """

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique event ID")
    event_name: str = Field(..., description="Event name (service.domain.action)")
    event_version: str = Field(default="1.0", description="Schema version")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="UTC timestamp of event creation",
    )
    producer: str = Field(..., description="Originating service name")
    correlation_id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        description="Request correlation ID for distributed tracing",
    )
    payload: dict[str, Any] = Field(default_factory=dict, description="Event-specific data")

    model_config = {"ser_json_timedelta": "iso8601"}
