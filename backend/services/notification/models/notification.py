import enum
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.shared.database.base_reexport import Base, TimestampMixin, UUIDMixin


class NotificationType(str, enum.Enum):
    SYSTEM = "SYSTEM"
    BOOKING = "BOOKING"
    DISPATCH = "DISPATCH"
    SURGE = "SURGE"
    PROMO = "PROMO"


class NotificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class NotificationChannel(str, enum.Enum):
    PUSH = "PUSH"
    EMAIL = "EMAIL"
    SMS = "SMS"
    IN_APP = "IN_APP"


class NotificationTemplate(UUIDMixin, TimestampMixin, Base):
    """Stores rendering templates and default channels for events."""

    __tablename__ = "notification_templates"

    event_type: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    channels: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    title_template: Mapped[str] = mapped_column(String(255), nullable=False)
    message_template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Notification(UUIDMixin, TimestampMixin, Base):
    """Tracks individual outbound notifications to users."""

    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType), nullable=False, index=True
    )
    channel: Mapped[NotificationChannel] = mapped_column(Enum(NotificationChannel), nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), default=NotificationStatus.PENDING, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=True)

    event_id: Mapped[str] = mapped_column(
        String(100), index=True, nullable=True
    )  # Used for idempotency mapping
    error_message: Mapped[str] = mapped_column(Text, nullable=True)

    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
