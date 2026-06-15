"""
AirLynk — API tests for Auth routes.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def auth_client() -> AsyncGenerator[AsyncClient, None]:
    """Test client with mocked infrastructure and mocked AuthRepository/Redis."""
    from backend.main import create_app
    from backend.shared.cache.redis_client import get_redis
    from backend.shared.database.session import get_db_session

    app = create_app()

    async def mock_get_db_session() -> AsyncGenerator[AsyncMock, None]:
        session = AsyncMock()
        yield session

    async def mock_get_redis() -> AsyncGenerator[AsyncMock, None]:
        redis = AsyncMock()
        yield redis

    app.dependency_overrides[get_db_session] = mock_get_db_session
    app.dependency_overrides[get_redis] = mock_get_redis

    with (
        patch("backend.main.init_db", new_callable=AsyncMock),
        patch("backend.main.close_db", new_callable=AsyncMock),
        patch("backend.main.init_redis", new_callable=AsyncMock),
        patch("backend.main.close_redis", new_callable=AsyncMock),
        patch("backend.main.init_rabbitmq", new_callable=AsyncMock),
        patch("backend.main.close_rabbitmq", new_callable=AsyncMock),
        patch("backend.main.setup_tracing"),
        patch("backend.main.shutdown_tracing"),
    ):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as ac:
            yield ac


@pytest.mark.api
@pytest.mark.asyncio
async def test_register_api(auth_client: AsyncClient) -> None:
    """Test POST /api/v1/auth/register"""
    with patch(
        "backend.services.auth.service.auth_service.AuthService.register_user",
        new_callable=AsyncMock,
    ) as mock_register:
        from backend.services.auth.schemas.auth import UserResponse

        mock_register.return_value = UserResponse(
            id=uuid.uuid4(),
            email="api@example.com",
            is_active=True,
            role="customer",
            created_at="2026-06-13T00:00:00Z",
        )

        response = await auth_client.post(
            "/api/v1/auth/register",
            json={"email": "api@example.com", "password": "SecurePassword123!"},
        )

        assert response.status_code == 201
        assert response.json()["email"] == "api@example.com"
