"""
AirLynk — Unit tests for AuthService.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from backend.services.auth.models.user import Role, User
from backend.services.auth.repository.auth_repository import AuthRepository
from backend.services.auth.schemas.auth import UserCreate
from backend.services.auth.service.auth_service import AuthService


@pytest.fixture
def auth_repo(mock_db_session: AsyncMock) -> AuthRepository:
    """Mock AuthRepository."""
    repo = AuthRepository(mock_db_session)
    repo.get_user_by_email = AsyncMock(return_value=None)  # type: ignore[method-assign]
    repo.get_role_by_name = AsyncMock(return_value=Role(id=uuid.uuid4(), name="customer"))  # type: ignore[method-assign]

    async def mock_create(u: User) -> User:
        from datetime import UTC, datetime

        u.id = uuid.uuid4()
        u.is_active = True
        u.created_at = datetime.now(UTC)
        return u

    repo.create_user = AsyncMock(side_effect=mock_create)  # type: ignore[method-assign]
    repo.update_user = AsyncMock()  # type: ignore[method-assign]
    return repo


@pytest.fixture
def auth_service(auth_repo: AuthRepository, mock_redis: AsyncMock) -> AuthService:
    """AuthService with mocked repo and redis."""
    return AuthService(auth_repo, mock_redis)


@pytest.mark.asyncio
async def test_register_user_success(auth_service: AuthService) -> None:
    """Test successful user registration."""
    payload = UserCreate(email="test@example.com", password="SecurePassword123!")

    result = await auth_service.register_user(payload)

    assert result.email == "test@example.com"
    assert result.role == "customer"
    auth_service.repo.create_user.assert_called_once()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_register_user_already_exists(auth_service: AuthService) -> None:
    """Test registration when user already exists."""
    existing_user = User(email="test@example.com")
    auth_service.repo.get_user_by_email = AsyncMock(return_value=existing_user)  # type: ignore[method-assign]

    payload = UserCreate(email="test@example.com", password="SecurePassword123!")

    with pytest.raises(HTTPException) as exc_info:
        await auth_service.register_user(payload)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "User already exists"
