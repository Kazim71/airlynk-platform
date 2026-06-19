"""
AirLynk — Fleet API Routes.

CRUD endpoints for drivers and vehicles with RBAC enforcement.
Only operators and platform admins can manage the fleet.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.fleet.repository.fleet_repository import FleetRepository
from backend.services.fleet.schemas.fleet import (
    DriverCreate,
    DriverResponse,
    DriverUpdate,
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
)
from backend.services.fleet.service.fleet_service import FleetService
from backend.shared.database.session import get_db_session
from backend.shared.middleware.rbac import Role, require_roles

router = APIRouter(prefix="/fleet", tags=["Fleet"])


def get_fleet_service(
    session: AsyncSession = Depends(get_db_session),
) -> FleetService:
    repo = FleetRepository(session)
    return FleetService(repo)


# --- Driver Endpoints ---


@router.post("/drivers", response_model=DriverResponse, status_code=201)
async def create_driver(
    payload: DriverCreate,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: FleetService = Depends(get_fleet_service),
) -> Any:
    """Create a new driver profile linked to an existing user account."""
    return await service.create_driver(payload)


@router.get("/drivers", response_model=list[DriverResponse])
async def list_drivers(
    active_only: bool = Query(False, description="Filter to active drivers only"),
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: FleetService = Depends(get_fleet_service),
) -> Any:
    """List all drivers. Optionally filter by active status."""
    return await service.list_drivers(active_only=active_only)


@router.get("/drivers/{driver_id}", response_model=DriverResponse)
async def get_driver(
    driver_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: FleetService = Depends(get_fleet_service),
) -> Any:
    """Get a specific driver by ID."""
    return await service.get_driver(driver_id)


@router.patch("/drivers/{driver_id}", response_model=DriverResponse)
async def update_driver(
    driver_id: uuid.UUID,
    payload: DriverUpdate,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: FleetService = Depends(get_fleet_service),
) -> Any:
    """Update a driver's details. Supports partial updates."""
    return await service.update_driver(driver_id, payload)


# --- Vehicle Endpoints ---


@router.post("/vehicles", response_model=VehicleResponse, status_code=201)
async def create_vehicle(
    payload: VehicleCreate,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: FleetService = Depends(get_fleet_service),
) -> Any:
    """Create a new vehicle assigned to a driver."""
    return await service.create_vehicle(payload)


@router.get("/vehicles", response_model=list[VehicleResponse])
async def list_vehicles(
    driver_id: uuid.UUID | None = Query(None, description="Filter vehicles by driver"),
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: FleetService = Depends(get_fleet_service),
) -> Any:
    """List all vehicles. Optionally filter by driver."""
    return await service.list_vehicles(driver_id=driver_id)


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: FleetService = Depends(get_fleet_service),
) -> Any:
    """Get a specific vehicle by ID."""
    return await service.get_vehicle(vehicle_id)


@router.patch("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: uuid.UUID,
    payload: VehicleUpdate,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: FleetService = Depends(get_fleet_service),
) -> Any:
    """Update a vehicle's details. Supports partial updates."""
    return await service.update_vehicle(vehicle_id, payload)
