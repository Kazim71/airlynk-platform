"""
AirLynk — Auth Repository.

Data access layer for User and Role entities. No business logic allowed.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.auth.models.user import Role, User


class AuthRepository:
    """Repository for Authentication and Authorization models."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        """Fetch user by email, eager loading their role."""
        stmt = select(User).where(User.email == email).options(selectinload(User.role))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Fetch user by ID."""
        stmt = select(User).where(User.id == user_id).options(selectinload(User.role))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        """Persist a new user to the database."""
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_user(self, user: User) -> User:
        """Persist changes to an existing user."""
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_role_by_name(self, name: str) -> Role | None:
        """Fetch a role by its unique name."""
        stmt = select(Role).where(Role.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
