"""
AirLynk — Auth Service.

Business logic for user registration, authentication, and token management.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from redis.asyncio import Redis

from backend.services.auth.models.user import User
from backend.services.auth.repository.auth_repository import AuthRepository  # noqa: TC001
from backend.services.auth.schemas.auth import (
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from backend.shared.config.settings import get_settings
from backend.shared.exceptions.handlers import AuthenticationError
from backend.shared.messaging.rabbitmq import publish_event
from backend.shared.security.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from backend.shared.security.password import hash_password, verify_password

logger = logging.getLogger(__name__)


class AuthService:
    """Service layer for authentication."""

    def __init__(self, repo: AuthRepository, redis: Redis) -> None:  # type: ignore[type-arg]
        self.repo = repo
        self.redis = redis
        self.settings = get_settings()

    async def register_user(self, payload: UserCreate) -> UserResponse:
        """Register a new user."""
        existing_user = await self.repo.get_user_by_email(payload.email)
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")

        # By default, assign 'customer' role
        role = await self.repo.get_role_by_name("customer")
        role_id = role.id if role else None

        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            role_id=role_id,
        )

        created_user = await self.repo.create_user(user)

        # Publish event
        await publish_event("auth.user.registered", {"user_id": str(created_user.id)})

        logger.info("User registered successfully", extra={"user_id": str(created_user.id)})

        return UserResponse(
            id=created_user.id,
            email=created_user.email,
            is_active=created_user.is_active,
            role=role.name if role else None,
            created_at=created_user.created_at,
        )

    async def authenticate_user(self, payload: UserLogin) -> TokenResponse:
        """Authenticate user and issue tokens."""
        user = await self.repo.get_user_by_email(payload.email)

        if not user or not user.is_active:
            raise AuthenticationError(message="Invalid email or password")

        # Check lockout
        if user.locked_until and user.locked_until > datetime.now(UTC):
            raise AuthenticationError(message="Account is locked. Try again later.")

        if not verify_password(payload.password, user.hashed_password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.now(UTC) + timedelta(minutes=15)
                await self.repo.update_user(user)
                await publish_event("auth.user.locked", {"user_id": str(user.id)})
            else:
                await self.repo.update_user(user)
            await publish_event("auth.user.login_failed", {"user_id": str(user.id)})
            raise AuthenticationError(message="Invalid email or password")

        # Reset failures on success
        if user.failed_login_attempts > 0 or user.locked_until:
            user.failed_login_attempts = 0
            user.locked_until = None
            await self.repo.update_user(user)

        role_name = user.role.name if user.role else "customer"
        permissions = [p.name for p in user.role.permissions] if user.role else []
        extra_claims = {"role": role_name, "permissions": permissions}

        access_token = create_access_token(subject=str(user.id), extra_claims=extra_claims)
        refresh_token = create_refresh_token(subject=str(user.id))

        # Store refresh token jti in redis
        decoded_refresh = decode_token(refresh_token)
        jti = decoded_refresh["jti"]
        exp = int(decoded_refresh["exp"] - datetime.now(UTC).timestamp())

        await self.redis.setex(f"refresh_token:{jti}", exp, str(user.id))

        await publish_event("auth.user.login_success", {"user_id": str(user.id)})
        logger.info("User authenticated", extra={"user_id": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",  # noqa: S106
        )

    async def refresh_token(self, payload: RefreshTokenRequest) -> TokenResponse:
        """Rotate access and refresh tokens."""
        try:
            decoded = decode_token(payload.refresh_token)
        except AuthenticationError:
            raise AuthenticationError(message="Invalid refresh token")  # noqa: B904

        if decoded.get("type") != "refresh":
            raise AuthenticationError(message="Invalid token type")

        jti = decoded.get("jti")
        user_id_str = decoded.get("sub")

        # Validate against Redis
        redis_key = f"refresh_token:{jti}"
        stored_user = await self.redis.get(redis_key)
        if not stored_user or stored_user != user_id_str:
            raise AuthenticationError(message="Refresh token revoked or invalid")

        user = await self.repo.get_user_by_id(uuid.UUID(user_id_str))
        if not user or not user.is_active:
            raise AuthenticationError(message="User inactive or deleted")

        # Invalidate old refresh token
        await self.redis.delete(redis_key)

        # Create new tokens
        role_name = user.role.name if user.role else "customer"
        permissions = [p.name for p in user.role.permissions] if user.role else []
        extra_claims = {"role": role_name, "permissions": permissions}

        new_access = create_access_token(subject=str(user.id), extra_claims=extra_claims)
        new_refresh = create_refresh_token(subject=str(user.id))

        new_decoded = decode_token(new_refresh)
        new_jti = new_decoded["jti"]
        exp = int(new_decoded["exp"] - datetime.now(UTC).timestamp())

        await self.redis.setex(f"refresh_token:{new_jti}", exp, str(user.id))

        await publish_event("auth.token.refreshed", {"user_id": str(user.id)})

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="bearer",  # noqa: S106
        )

    async def logout(self, refresh_token: str) -> None:
        """Invalidate the refresh token."""
        try:
            decoded = decode_token(refresh_token)
            jti = decoded.get("jti")
            if jti:
                await self.redis.delete(f"refresh_token:{jti}")

            # Note: The frontend is expected to discard the access token.
            # If aggressive revocation is needed, we could add the access token JTI to a Redis blocklist here.  # noqa: E501
        except AuthenticationError:
            # Ignore errors during logout (e.g. token already expired)
            pass
