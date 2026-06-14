"""
AirLynk — Shared FastAPI dependencies.

Centralised dependency providers following CODING_STANDARDS.md §6:
  "Use FastAPI dependency system only."
"""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.cache.redis_client import get_redis
from backend.shared.config.settings import Settings, get_settings
from backend.shared.database.session import get_db_session
from backend.shared.middleware.rbac import get_current_user

# --- Type-aliased dependencies for cleaner route signatures ----------------

DBSession = Annotated[AsyncSession, Depends(get_db_session)]
RedisClient = Annotated[Redis, Depends(get_redis)]
AppSettings = Annotated[Settings, Depends(get_settings)]
CurrentUser = Annotated[dict[str, Any], Depends(get_current_user)]
