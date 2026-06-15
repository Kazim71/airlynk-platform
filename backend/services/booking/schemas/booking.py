"""
AirLynk — Booking Schemas.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from backend.services.booking.models.booking import BookingStatus, TripStatus


class TripResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    trip_status: TripStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
    actual_distance_km: float | None = None
    actual_duration_minutes: int | None = None

    model_config = ConfigDict(from_attributes=True)


class BookingStatusHistoryResponse(BaseModel):
    id: uuid.UUID
    old_status: str | None = None
    new_status: str
    changed_by: uuid.UUID
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BookingBase(BaseModel):
    pickup_location: str = Field(..., max_length=255)
    dropoff_location: str = Field(..., max_length=255)
    scheduled_time: datetime
    passenger_count: int = Field(default=1, ge=1, le=8)


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    pickup_location: str | None = Field(None, max_length=255)
    dropoff_location: str | None = Field(None, max_length=255)
    scheduled_time: datetime | None = None
    passenger_count: int | None = Field(None, ge=1, le=8)


class AssignDriverRequest(BaseModel):
    driver_id: uuid.UUID
    vehicle_id: uuid.UUID


class BookingResponse(BookingBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    booking_status: BookingStatus
    assigned_driver_id: uuid.UUID | None = None
    vehicle_id: uuid.UUID | None = None
    estimated_price: float
    created_at: datetime
    updated_at: datetime

    trip: TripResponse | None = None
    status_history: list[BookingStatusHistoryResponse] | None = None

    model_config = ConfigDict(from_attributes=True)
