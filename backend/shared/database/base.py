"""
AirLynk — SQLAlchemy Declarative Base & common mixins.

All ORM models inherit from ``Base``.  The mixins provide a consistent set of
columns across the entire platform (UUID primary keys, audit timestamps).

See CODING_STANDARDS.md §8 and SERVICE_TEMPLATE.md §10.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, MetaData, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Consistent naming convention for constraints — critical for Alembic
# auto-generation to produce deterministic migration names.
NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Project-wide declarative base with naming conventions."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # Make all models JSON-serialisable for debugging (not for API responses).
    def to_dict(self) -> dict[str, Any]:
        """Shallow dict of mapped column values."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class UUIDMixin:
    """UUID v4 primary key mixin."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        sort_order=-10,
    )


class TimestampMixin:
    """Audit timestamp mixin — ``created_at`` and ``updated_at``."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
        sort_order=900,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
        sort_order=901,
    )
