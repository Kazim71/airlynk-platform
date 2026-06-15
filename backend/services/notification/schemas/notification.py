"""
AirLynk — Notification Schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.services.notification.models.notification import (
    DeliveryStatus,
    NotificationChannel,
    NotificationStatus,
)


class NotificationDeliveryResponse(BaseModel):
    """Schema for a single delivery attempt."""

    id: uuid.UUID
    notification_id: uuid.UUID
    channel: NotificationChannel
    status: DeliveryStatus
    attempt_count: int
    error_message: str | None = None
    sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationBase(BaseModel):
    """Base notification data."""

    title: str = Field(..., max_length=255)
    content: str
    metadata_payload: dict[str, Any] | None = None


class NotificationCreate(NotificationBase):
    """Payload to create a new notification."""

    user_id: uuid.UUID


class NotificationResponse(NotificationBase):
    """Response schema for a notification."""

    id: uuid.UUID
    user_id: uuid.UUID
    status: NotificationStatus
    read_at: datetime | None = None
    deliveries: list[NotificationDeliveryResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationTemplateResponse(BaseModel):
    """Schema for a notification template."""

    id: uuid.UUID
    event_name: str
    channel: NotificationChannel
    subject_template: str | None = None
    body_template: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserNotificationPreferenceResponse(BaseModel):
    """User notification preferences."""

    id: uuid.UUID
    user_id: uuid.UUID
    email_enabled: bool
    sms_enabled: bool
    push_enabled: bool

    model_config = ConfigDict(from_attributes=True)


class UserNotificationPreferenceUpdate(BaseModel):
    """Payload to update notification preferences."""

    email_enabled: bool | None = None
    sms_enabled: bool | None = None
    push_enabled: bool | None = None
