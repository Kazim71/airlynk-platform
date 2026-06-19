"""
AirLynk — Fleet Service.

Business logic layer for Driver and Vehicle management.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import HTTPException

from backend.services.fleet.models.fleet import Driver, Vehicle
from backend.services.fleet.repository.fleet_repository import FleetRepository
from backend.services.fleet.schemas.fleet import (
    DriverCreate,
    DriverUpdate,
    VehicleCreate,
    VehicleUpdate,
)
from backend.shared.exceptions.handlers import ConflictError, NotFoundError

logger = logging.getLogger(__name__)


class FleetService:
    """Service layer for fleet management."""

    def __init__(self, repo: FleetRepository) -> None:
        self.repo = repo

    # --- Driver Operations ---

    async def create_driver(self, data: DriverCreate) -> Driver:
        """Create a new driver profile."""
        existing = await self.repo.get_driver_by_user_id(data.user_id)
        if existing:
            raise ConflictError("Driver profile already exists for this user")

        driver = Driver(
            user_id=data.user_id,
            license_number=data.license_number,
            is_active=data.is_active,
            is_available=data.is_available,
        )
        created = await self.repo.create_driver(driver)
        logger.info(f"Driver {created.id} created for user {data.user_id}")
        return created

    async def get_driver(self, driver_id: uuid.UUID) -> Driver:
        driver = await self.repo.get_driver_by_id(driver_id)
        if not driver:
            raise NotFoundError("Driver not found")
        return driver

    async def list_drivers(self, active_only: bool = False) -> list[Driver]:
        drivers = await self.repo.list_drivers(active_only=active_only)
        return list(drivers)

    async def update_driver(self, driver_id: uuid.UUID, data: DriverUpdate) -> Driver:
        driver = await self.repo.get_driver_by_id(driver_id)
        if not driver:
            raise NotFoundError("Driver not found")

        if data.license_number is not None:
            driver.license_number = data.license_number
        if data.is_active is not None:
            driver.is_active = data.is_active
        if data.is_available is not None:
            driver.is_available = data.is_available

        updated = await self.repo.update_driver(driver)
        logger.info(f"Driver {driver_id} updated")
        return updated

    # --- Vehicle Operations ---

    async def create_vehicle(self, data: VehicleCreate) -> Vehicle:
        """Create a new vehicle assigned to a driver."""
        # Verify driver exists
        driver = await self.repo.get_driver_by_id(data.driver_id)
        if not driver:
            raise NotFoundError("Driver not found")

        vehicle = Vehicle(
            driver_id=data.driver_id,
            make=data.make,
            model=data.model,
            license_plate=data.license_plate,
        )
        created = await self.repo.create_vehicle(vehicle)
        logger.info(f"Vehicle {created.id} created for driver {data.driver_id}")
        return created

    async def get_vehicle(self, vehicle_id: uuid.UUID) -> Vehicle:
        vehicle = await self.repo.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError("Vehicle not found")
        return vehicle

    async def list_vehicles(self, driver_id: uuid.UUID | None = None) -> list[Vehicle]:
        vehicles = await self.repo.list_vehicles(driver_id=driver_id)
        return list(vehicles)

    async def update_vehicle(self, vehicle_id: uuid.UUID, data: VehicleUpdate) -> Vehicle:
        vehicle = await self.repo.get_vehicle_by_id(vehicle_id)
        if not vehicle:
            raise NotFoundError("Vehicle not found")

        if data.make is not None:
            vehicle.make = data.make
        if data.model is not None:
            vehicle.model = data.model
        if data.license_plate is not None:
            vehicle.license_plate = data.license_plate

        updated = await self.repo.update_vehicle(vehicle)
        logger.info(f"Vehicle {vehicle_id} updated")
        return updated
