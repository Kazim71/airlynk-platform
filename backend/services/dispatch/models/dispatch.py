"""
AirLynk — Dispatch Models.

Defines the state of dispatch requests and driver ping attempts.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.database.base import Base, TimestampMixin


class DispatchStatus(enum.StrEnum):
    PENDING = "pending"
    ASSIGNING = "assigning"
    ASSIGNED = "assigned"
    FAILED = "failed"
    ESCALATED = "escalated"


class AttemptStatus(enum.StrEnum):
    OFFERED = "offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


class DispatchRequest(Base, TimestampMixin):
    """Overall state of dispatching a driver for a specific booking."""

    __tablename__ = "dispatch_requests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    status: Mapped[DispatchStatus] = mapped_column(
        Enum(DispatchStatus, name="dispatch_status_enum", create_constraint=True),
        default=DispatchStatus.PENDING,
        nullable=False,
        index=True,
    )
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    attempts: Mapped[list[DispatchAttempt]] = relationship(
        back_populates="dispatch_request", cascade="all, delete-orphan"
    )


class DispatchAttempt(Base, TimestampMixin):
    """An individual ping/offer to a specific driver."""

    __tablename__ = "dispatch_attempts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dispatch_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dispatch_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("drivers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[AttemptStatus] = mapped_column(
        Enum(AttemptStatus, name="attempt_status_enum", create_constraint=True),
        default=AttemptStatus.OFFERED,
        nullable=False,
        index=True,
    )

    # Relationships
    dispatch_request: Mapped[DispatchRequest] = relationship(back_populates="attempts")
