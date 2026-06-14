"""
Tests for health and readiness endpoints.

These tests use HTTPX's AsyncClient to test the FastAPI app in-process,
mocking the infrastructure dependencies that aren't available in CI.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client with mocked infrastructure."""
    # Mock all infrastructure init/close to avoid requiring real services
    with (
        patch("backend.services.api.app.main.init_db", new_callable=AsyncMock),
        patch("backend.services.api.app.main.close_db", new_callable=AsyncMock),
        patch("backend.services.api.app.main.init_redis", new_callable=AsyncMock),
        patch("backend.services.api.app.main.close_redis", new_callable=AsyncMock),
        patch("backend.services.api.app.main.init_rabbitmq", new_callable=AsyncMock),
        patch("backend.services.api.app.main.close_rabbitmq", new_callable=AsyncMock),
        patch("backend.services.api.app.main.setup_tracing"),
        patch("backend.services.api.app.main.shutdown_tracing"),
    ):
        from backend.services.api.app.main import create_app

        app = create_app()
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://testserver",
        ) as ac:
            yield ac


@pytest.mark.api
class TestHealthEndpoint:
    """Test the /health endpoint."""

    async def test_health_endpoint_returns_200(self, client: AsyncClient) -> None:
        with (
            patch(
                "backend.services.api.app.api.routes.health._check_postgres",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "backend.services.api.app.api.routes.health.redis_health_check",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "backend.services.api.app.api.routes.health.rabbitmq_health_check",
                new_callable=AsyncMock,
                return_value=True,
            ),
        ):
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["status"] == "healthy"
            assert data["data"]["postgres"] is True
            assert data["data"]["redis"] is True
            assert data["data"]["rabbitmq"] is True

    async def test_health_degraded_when_redis_down(self, client: AsyncClient) -> None:
        with (
            patch(
                "backend.services.api.app.api.routes.health._check_postgres",
                new_callable=AsyncMock,
                return_value=True,
            ),
            patch(
                "backend.services.api.app.api.routes.health.redis_health_check",
                new_callable=AsyncMock,
                return_value=False,
            ),
            patch(
                "backend.services.api.app.api.routes.health.rabbitmq_health_check",
                new_callable=AsyncMock,
                return_value=True,
            ),
        ):
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["data"]["status"] == "degraded"
            assert data["data"]["redis"] is False


@pytest.mark.api
class TestReadinessEndpoint:
    """Test the /ready endpoint."""

    async def test_readiness_returns_200(self, client: AsyncClient) -> None:
        response = await client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.api
class TestMetricsEndpoint:
    """Test the /metrics endpoint."""

    async def test_metrics_returns_prometheus_format(self, client: AsyncClient) -> None:
        response = await client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
