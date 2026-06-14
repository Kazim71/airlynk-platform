"""
AirLynk — Standard API response schemas.

All endpoints MUST use these wrappers for consistency with the documented
response format in API_SPEC.md.

Success::

    {"success": true, "message": "Request successful", "data": {...}}

Error::

    {"success": false, "message": "Validation failed", "errors": [...]}
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper."""

    success: bool = Field(default=True)
    message: str = Field(default="Request successful")
    data: T | None = Field(default=None)


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""

    success: bool = Field(default=False)
    message: str = Field(default="An error occurred")
    errors: list[Any] = Field(default_factory=list)


class HealthStatus(BaseModel):
    """Health check response payload."""

    status: str = Field(default="healthy")
    postgres: bool = Field(default=False)
    redis: bool = Field(default=False)
    rabbitmq: bool = Field(default=False)


class PaginatedMeta(BaseModel):
    """Pagination metadata for list endpoints."""

    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)
