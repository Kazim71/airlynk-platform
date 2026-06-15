"""
AirLynk — Notification Models.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.database.base import Base, TimestampMixin


class NotificationChannel(enum.StrEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBSOCKET = "websocket"


class NotificationStatus(enum.StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    PARTIAL = "partial"


class DeliveryStatus(enum.StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"


class NotificationTemplate(Base, TimestampMixin):
    """Stores Jinja2-style templates for notifications."""

    __tablename__ = "notification_templates"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, name="notification_channel_enum", create_constraint=True),
        nullable=False,
    )
    subject_template: Mapped[str | None] = mapped_column(String(255), nullable=True)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class UserNotificationPreference(Base, TimestampMixin):
    """User toggles for communication channels."""

    __tablename__ = "user_notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sms_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    push_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Notification(Base, TimestampMixin):
    """A user-facing notification."""

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, name="notification_status_enum", create_constraint=True),
        default=NotificationStatus.PENDING,
        nullable=False,
        index=True,
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    deliveries: Mapped[list[NotificationDelivery]] = relationship(
        back_populates="notification", cascade="all, delete-orphan"
    )


class NotificationDelivery(Base, TimestampMixin):
    """Tracks delivery attempts across providers."""

    __tablename__ = "notification_deliveries"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    notification_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, name="notification_channel_enum", create_constraint=False),
        nullable=False,
    )
    status: Mapped[DeliveryStatus] = mapped_column(
        Enum(DeliveryStatus, name="delivery_status_enum", create_constraint=True),
        default=DeliveryStatus.PENDING,
        nullable=False,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    notification: Mapped[Notification] = relationship(back_populates="deliveries")
