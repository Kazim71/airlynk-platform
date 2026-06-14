"""
AirLynk — Async Redis client.

Manages a shared Redis connection pool for caching, session storage, and
rate-limiting.  See ARCHITECTURE.md §5 (Cache Layer) and SECURITY.md §4.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from typing import Any

from redis.asyncio import ConnectionPool, Redis

from backend.shared.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

_pool: ConnectionPool[Any] | None = None
_client: Redis | None = None  # type: ignore[type-arg]


async def init_redis(settings: Settings | None = None) -> None:
    """Create the Redis connection pool — called during startup."""
    global _pool, _client
    settings = settings or get_settings()
    _pool = ConnectionPool.from_url(
        settings.redis_url,
        decode_responses=True,
        max_connections=20,
    )
    _client = Redis(connection_pool=_pool)
    logger.info("Redis connection pool initialised")


async def close_redis() -> None:
    """Tear down the pool — called during shutdown."""
    global _pool, _client
    if _client is not None:
        await _client.close()
    if _pool is not None:
        await _pool.disconnect()
    _client = None
    _pool = None
    logger.info("Redis connection pool closed")


async def get_redis() -> AsyncGenerator[Redis, None]:  # type: ignore[type-arg]
    """FastAPI dependency — yields a Redis client."""
    if _client is None:
        msg = "Redis not initialised. Call init_redis() during startup."
        raise RuntimeError(msg)
    yield _client


def get_redis_client() -> Redis:  # type: ignore[type-arg]
    """Return the singleton client — for health checks and non-DI contexts."""
    if _client is None:
        msg = "Redis not initialised."
        raise RuntimeError(msg)
    return _client


async def redis_health_check() -> bool:
    """Return True if Redis responds to PING."""
    try:
        client = get_redis_client()
        return bool(await client.ping())
    except Exception:
        return False
