"""
AirLynk — Auth API Schemas.

Pydantic v2 models for authentication requests and responses.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Payload for registering a new user."""

    email: EmailStr
    password: str = Field(min_length=12, description="Password must be at least 12 characters")
    role: str = Field(default="customer", description="User role: customer, driver, operator")


class UserLogin(BaseModel):
    """Payload for authenticating a user."""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Payload for rotating tokens."""

    refresh_token: str


class TokenResponse(BaseModel):
    """Response containing access and refresh JWTs."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Standard user response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    is_active: bool
    role: str | None = None
    created_at: datetime
