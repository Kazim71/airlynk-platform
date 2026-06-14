"""
AirLynk — Shared pytest fixtures.

Provides reusable fixtures for unit and API tests:
  - Test settings (overridden for isolation)
  - AsyncClient for API testing
  - Event loop configuration
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend.shared.config.settings import Settings, override_settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test-specific settings that don't require real infrastructure."""
    return override_settings(
        {
            "APP_NAME": "airlynk-test",
            "APP_ENV": "development",
            "APP_DEBUG": "true",
            "APP_LOG_LEVEL": "DEBUG",
            "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/airlynk_test",
            "REDIS_URL": "redis://localhost:6379/1",
            "RABBITMQ_URL": "amqp://guest:guest@localhost:5672/",
            "JWT_SECRET": "test-secret-key-for-unit-tests-only-32chars",
        }
    )


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock async database session for unit tests."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_redis() -> AsyncMock:
    """Mock Redis client for unit tests."""
    redis = AsyncMock()
    redis.ping = AsyncMock(return_value=True)
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    return redis


@pytest.fixture
def sample_event_payload() -> dict[str, Any]:
    """Sample event envelope payload for testing."""
    return {
        "event_name": "auth.user.login_success",
        "event_version": "1.0",
        "producer": "auth-service",
        "payload": {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "ip_address": "127.0.0.1",
        },
    }
