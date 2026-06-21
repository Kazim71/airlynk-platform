"""
AirLynk — Geo Schemas.
"""

from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    pickup_lat: float = Field(..., ge=-90, le=90)
    pickup_lng: float = Field(..., ge=-180, le=180)
    dropoff_lat: float = Field(..., ge=-90, le=90)
    dropoff_lng: float = Field(..., ge=-180, le=180)


class RouteEstimateResponse(BaseModel):
    distance_km: float
    duration_minutes: int
    polyline: str | None = None
    is_surge_active: bool = False
