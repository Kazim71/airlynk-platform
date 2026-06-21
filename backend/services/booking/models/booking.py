"""
AirLynk — Booking & Trip Models.

Defines customer bookings and their associated operational trips,
plus booking status history for auditability.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.database.base import Base, TimestampMixin


class BookingStatus(enum.StrEnum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    PAYMENT_AUTHORIZED = "payment_authorized"
    DISPATCHING = "dispatching"
    DRIVER_ASSIGNED = "driver_assigned"
    DRIVER_EN_ROUTE = "driver_en_route"
    DRIVER_ARRIVED = "driver_arrived"
    PASSENGER_PICKED = "passenger_picked"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    NO_SHOW = "no_show"


class TripStatus(enum.StrEnum):
    PENDING = "pending"
    STARTED = "started"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Booking(Base, TimestampMixin):
    """Customer booking representation."""

    __tablename__ = "bookings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    pickup_location: Mapped[str] = mapped_column(String(255), nullable=False)
    pickup_lat: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False, server_default="0.0")
    pickup_lng: Mapped[float] = mapped_column(Numeric(10, 6), nullable=False, server_default="0.0")
    dropoff_location: Mapped[str] = mapped_column(String(255), nullable=False)
    dropoff_lat: Mapped[float] = mapped_column(
        Numeric(10, 6), nullable=False, server_default="0.0"
    )
    dropoff_lng: Mapped[float] = mapped_column(
        Numeric(10, 6), nullable=False, server_default="0.0"
    )
    scheduled_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    passenger_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    booking_status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status_enum", create_constraint=True),
        default=BookingStatus.CREATED,
        nullable=False,
        index=True,
    )
    assigned_driver_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True, index=True
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True
    )
    estimated_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    trip: Mapped[Trip] = relationship(back_populates="booking", uselist=False)
    status_history: Mapped[list[BookingStatusHistory]] = relationship(
        back_populates="booking", cascade="all, delete-orphan"
    )


class Trip(Base, TimestampMixin):
    """Operational execution of a booking."""

    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    trip_status: Mapped[TripStatus] = mapped_column(
        Enum(TripStatus, name="trip_status_enum", create_constraint=True),
        default=TripStatus.PENDING,
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_distance_km: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    actual_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    booking: Mapped[Booking] = relationship(back_populates="trip")


class BookingStatusHistory(Base, TimestampMixin):
    """Audit log of booking status transitions."""

    __tablename__ = "booking_status_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    old_status: Mapped[str] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(), nullable=False
    )

    # Relationships
    booking: Mapped[Booking] = relationship(back_populates="status_history")
