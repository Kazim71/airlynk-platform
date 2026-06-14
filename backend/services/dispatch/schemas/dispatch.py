"""
AirLynk — Dispatch Domain Schemas.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.services.dispatch.models.dispatch import AttemptStatus, DispatchStatus


class DispatchRequestSchema(BaseModel):
    """Schema for returning a dispatch request state."""

    id: UUID
    booking_id: UUID
    status: DispatchStatus
    retry_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DispatchAttemptSchema(BaseModel):
    """Schema for returning an individual dispatch attempt."""

    id: UUID
    dispatch_request_id: UUID
    driver_id: UUID
    status: AttemptStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DriverAvailabilityUpdate(BaseModel):
    """Schema for a driver updating their availability status."""

    driver_id: UUID
    is_available: bool = Field(description="Whether the driver is ready to accept rides")
    latitude: float | None = Field(None, description="Current latitude if available")
    longitude: float | None = Field(None, description="Current longitude if available")


class DispatchDecision(BaseModel):
    """Schema for a driver accepting or rejecting an assignment."""

    attempt_id: UUID
    accepted: bool = Field(description="True to accept, False to reject")


class DispatchMetrics(BaseModel):
    """Schema for exposing dispatch health metrics."""

    active_requests: int
    failed_requests: int
    escalated_requests: int
    average_retries: float
