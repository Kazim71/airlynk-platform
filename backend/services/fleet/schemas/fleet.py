"""
AirLynk — Fleet Domain Schemas.

Pydantic v2 models for driver and vehicle management.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# --- Driver Schemas ---


class DriverCreate(BaseModel):
    """Create a new driver profile linked to an existing user."""

    user_id: uuid.UUID
    license_number: str = Field(..., min_length=3, max_length=50)
    is_active: bool = Field(default=True)
    is_available: bool = Field(default=False)


class DriverUpdate(BaseModel):
    """Partial update for a driver."""

    license_number: str | None = Field(None, min_length=3, max_length=50)
    is_active: bool | None = None
    is_available: bool | None = None


class DriverResponse(BaseModel):
    """Driver response including vehicles."""

    id: uuid.UUID
    user_id: uuid.UUID
    license_number: str
    is_active: bool
    is_available: bool
    created_at: datetime
    updated_at: datetime
    vehicles: list[VehicleResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- Vehicle Schemas ---


class VehicleCreate(BaseModel):
    """Create a new vehicle assigned to a driver."""

    driver_id: uuid.UUID
    make: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    license_plate: str = Field(..., min_length=1, max_length=50)


class VehicleUpdate(BaseModel):
    """Partial update for a vehicle."""

    make: str | None = Field(None, min_length=1, max_length=100)
    model: str | None = Field(None, min_length=1, max_length=100)
    license_plate: str | None = Field(None, min_length=1, max_length=50)


class VehicleResponse(BaseModel):
    """Vehicle response."""

    id: uuid.UUID
    driver_id: uuid.UUID
    make: str
    model: str
    license_plate: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Rebuild DriverResponse to resolve the forward reference
DriverResponse.model_rebuild()
