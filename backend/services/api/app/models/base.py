"""
AirLynk — Service-level model base.

Re-exports the shared ``Base``, ``UUIDMixin``, and ``TimestampMixin`` so that
service-specific models can import from a single location.

All future ORM models for this service should inherit from
``Base`` + ``UUIDMixin`` + ``TimestampMixin``.
"""

from backend.shared.database.base import Base, TimestampMixin, UUIDMixin

__all__ = ["Base", "TimestampMixin", "UUIDMixin"]
