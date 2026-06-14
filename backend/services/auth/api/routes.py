"""
AirLynk — Auth API Routes.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.auth.repository.auth_repository import AuthRepository
from backend.services.auth.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from backend.services.auth.service.auth_service import AuthService
from backend.shared.cache.redis_client import get_redis
from backend.shared.database.session import get_db_session
from backend.shared.middleware.rbac import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),  # type: ignore[type-arg]
) -> AuthService:
    """Dependency injection for AuthService."""
    repo = AuthRepository(session)
    return AuthService(repo, redis)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    payload: UserCreate,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user account."""
    return await service.register_user(payload)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: UserLogin,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate and issue access & refresh tokens."""
    return await service.authenticate_user(payload)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Rotate tokens using a valid refresh token."""
    return await service.refresh_token(payload)


@router.post("/logout", status_code=204)
async def logout(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> None:
    """Invalidate a refresh token."""
    await service.logout(payload.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict[str, Any] = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Get the currently authenticated user's profile."""
    user_id = uuid.UUID(current_user["sub"])
    user = await service.repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        role=user.role.name if user.role else None,
        created_at=user.created_at,
    )
