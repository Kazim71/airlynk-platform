"""
AirLynk — Realtime Domain Schemas.
"""

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class LocationUpdate(BaseModel):
    """Payload representing a driver's live GPS location update."""

    lat: float = Field(..., description="Latitude", ge=-90.0, le=90.0)
    lng: float = Field(..., description="Longitude", ge=-180.0, le=180.0)
    heading: float | None = Field(None, description="Heading in degrees (0-360)")
    speed: float | None = Field(None, description="Speed in meters/second")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RealtimeEvent(BaseModel):
    """Payload representing a realtime event pushed over WebSocket."""

    event: str = Field(..., description="Name of the event (e.g., booking.updated)")
    data: dict[str, Any] = Field(default_factory=dict, description="Event data payload")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
