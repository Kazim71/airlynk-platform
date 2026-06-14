"""
AirLynk — Async SQLAlchemy session management.

Provides an async engine factory, a scoped session factory, and a FastAPI
dependency that yields a session per request.  Follows the async-first
pattern mandated in CODING_STANDARDS.md §12.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.shared.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _build_engine(settings: Settings) -> AsyncEngine:
    """Create an ``AsyncEngine`` from application settings."""
    return create_async_engine(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_pre_ping=True,
        echo=settings.app_debug,
    )


async def init_db(settings: Settings | None = None) -> None:
    """Initialise the async engine and session factory.

    Called once during application startup.
    """
    global _engine, _session_factory
    settings = settings or get_settings()
    _engine = _build_engine(settings)
    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    logger.info("Database engine initialised", extra={"database_url": "***"})


async def close_db() -> None:
    """Dispose of the async engine — called during shutdown."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        logger.info("Database engine disposed")
    _engine = None
    _session_factory = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an ``AsyncSession`` per request."""
    if _session_factory is None:
        msg = "Database not initialised. Call init_db() during startup."
        raise RuntimeError(msg)
    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_engine() -> AsyncEngine:
    """Return the current engine — used for health checks."""
    if _engine is None:
        msg = "Database not initialised."
        raise RuntimeError(msg)
    return _engine
