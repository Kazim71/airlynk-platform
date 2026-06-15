"""
AirLynk — Pricing Domain Schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PricingRuleBase(BaseModel):
    city: str = Field(..., max_length=100)
    vehicle_type: str = Field(..., max_length=50)
    base_fare: Decimal = Field(..., ge=0)
    per_km_rate: Decimal = Field(..., ge=0)
    per_minute_rate: Decimal = Field(..., ge=0)
    minimum_fare: Decimal = Field(..., ge=0)
    waiting_charge_per_minute: Decimal = Field(default=Decimal("0.00"), ge=0)
    cancellation_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    surge_multiplier: Decimal = Field(default=Decimal("1.00"), ge=1.0)
    airport_fee: Decimal = Field(default=Decimal("0.00"), ge=0)
    active: bool = Field(default=True)


class PricingRuleCreate(PricingRuleBase):
    pass


class PricingRuleUpdate(BaseModel):
    base_fare: Decimal | None = Field(None, ge=0)
    per_km_rate: Decimal | None = Field(None, ge=0)
    per_minute_rate: Decimal | None = Field(None, ge=0)
    minimum_fare: Decimal | None = Field(None, ge=0)
    waiting_charge_per_minute: Decimal | None = Field(None, ge=0)
    cancellation_fee: Decimal | None = Field(None, ge=0)
    surge_multiplier: Decimal | None = Field(None, ge=1.0)
    airport_fee: Decimal | None = Field(None, ge=0)
    active: bool | None = Field(None)


class PricingRuleResponse(PricingRuleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FareEstimateRequest(BaseModel):
    pickup_lat: float = Field(..., ge=-90, le=90)
    pickup_lon: float = Field(..., ge=-180, le=180)
    dropoff_lat: float = Field(..., ge=-90, le=90)
    dropoff_lon: float = Field(..., ge=-180, le=180)
    city: str = Field(..., max_length=100)
    vehicle_type: str = Field(..., max_length=50)
    estimated_duration_minutes: int = Field(..., ge=1)
    estimated_distance_km: Decimal = Field(..., ge=0)
    is_airport: bool = Field(default=False)
    booking_id: uuid.UUID | None = None


class FareEstimateResponse(BaseModel):
    id: uuid.UUID | None = None
    booking_id: uuid.UUID | None = None
    pricing_rule_id: uuid.UUID
    estimated_distance_km: Decimal
    estimated_duration_minutes: int
    base_fare: Decimal
    distance_fare: Decimal
    time_fare: Decimal
    airport_fee: Decimal
    surge_applied: Decimal
    subtotal: Decimal
    total_estimate: Decimal
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
