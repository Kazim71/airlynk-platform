"""
AirLynk — Fleet Repository.

Data access layer for Drivers and Vehicles.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.fleet.models.fleet import Driver, Vehicle


class FleetRepository:
    """Encapsulates data access for Driver and Vehicle entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # --- Driver Operations ---

    async def create_driver(self, driver: Driver) -> Driver:
        self.session.add(driver)
        await self.session.commit()
        stmt = (
            select(Driver)
            .options(selectinload(Driver.vehicles))
            .where(Driver.id == driver.id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_driver_by_id(self, driver_id: uuid.UUID) -> Driver | None:
        stmt = (
            select(Driver)
            .options(selectinload(Driver.vehicles))
            .where(Driver.id == driver_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_driver_by_user_id(self, user_id: uuid.UUID) -> Driver | None:
        stmt = (
            select(Driver)
            .options(selectinload(Driver.vehicles))
            .where(Driver.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_drivers(
        self, active_only: bool = False, limit: int = 50, offset: int = 0
    ) -> Sequence[Driver]:
        stmt = (
            select(Driver)
            .options(selectinload(Driver.vehicles))
            .order_by(Driver.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if active_only:
            stmt = stmt.where(Driver.is_active.is_(True))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_driver(self, driver: Driver) -> Driver:
        await self.session.commit()
        await self.session.refresh(driver)
        return driver

    # --- Vehicle Operations ---

    async def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        self.session.add(vehicle)
        await self.session.commit()
        await self.session.refresh(vehicle)
        return vehicle

    async def get_vehicle_by_id(self, vehicle_id: uuid.UUID) -> Vehicle | None:
        stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_vehicles(
        self, driver_id: uuid.UUID | None = None, limit: int = 50, offset: int = 0
    ) -> Sequence[Vehicle]:
        stmt = select(Vehicle).order_by(Vehicle.created_at.desc()).limit(limit).offset(offset)
        if driver_id:
            stmt = stmt.where(Vehicle.driver_id == driver_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
        await self.session.commit()
        await self.session.refresh(vehicle)
        return vehicle
