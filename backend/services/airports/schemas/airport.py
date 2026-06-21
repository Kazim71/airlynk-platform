"""
AirLynk — Airport Schemas.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AirportBase(BaseModel):
    code: str = Field(..., max_length=10)
    name: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    country: str = Field(default="India", max_length=100)
    latitude: float
    longitude: float
    timezone: str = Field(default="Asia/Kolkata", max_length=50)
    is_active: bool = True


class AirportCreate(AirportBase):
    pass


class AirportResponse(AirportBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
