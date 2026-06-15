"""
AirLynk — Pricing Domain Models.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from backend.shared.database.base_reexport import Base, TimestampMixin, UUIDMixin


class PricingRule(Base, UUIDMixin, TimestampMixin):
    """
    Pricing rules configurable by operators.
    Defines the base economic parameters for a city and vehicle type.
    """

    __tablename__ = "pricing_rules"

    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    vehicle_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    base_fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    per_km_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    per_minute_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    minimum_fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    waiting_charge_per_minute: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    cancellation_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
    surge_multiplier: Mapped[Decimal] = mapped_column(
        Numeric(4, 2), nullable=False, default=Decimal("1.00")
    )
    airport_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )

    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)


class FareEstimate(Base, UUIDMixin, TimestampMixin):
    """
    A generated fare estimate linked to a specific booking.
    """

    __tablename__ = "fare_estimates"

    booking_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    pricing_rule_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)

    estimated_distance_km: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estimated_duration_minutes: Mapped[int] = mapped_column(nullable=False)

    estimated_fare: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    surge_applied: Mapped[Decimal] = mapped_column(
        Numeric(4, 2), nullable=False, default=Decimal("1.00")
    )
