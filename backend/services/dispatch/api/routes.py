"""
AirLynk — Dispatch API Routes.

All dispatch endpoints are protected by JWT + RBAC.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from backend.services.booking.repository.booking_repository import BookingRepository
from backend.services.dispatch.repository.dispatch_repository import DispatchRepository
from backend.services.dispatch.schemas.dispatch import (
    DispatchDecision,
    DriverAvailabilityUpdate,
)
from backend.services.dispatch.service.dispatch_service import DispatchService
from backend.services.fleet.repository.fleet_repository import FleetRepository
from backend.shared.cache.redis_client import get_redis
from backend.shared.database.session import get_db_session
from backend.shared.exceptions.handlers import ValidationError
from backend.shared.middleware.rbac import Role, require_roles

router = APIRouter(prefix="/dispatch", tags=["dispatch"])


def get_dispatch_service(  # type: ignore
    session=Depends(get_db_session),
    redis=Depends(get_redis),
) -> DispatchService:
    return DispatchService(
        dispatch_repo=DispatchRepository(session),
        booking_repo=BookingRepository(session),
        fleet_repo=FleetRepository(session),
        redis_client=redis,
    )


@router.post("/availability", status_code=status.HTTP_200_OK)
async def update_availability(
    update: DriverAvailabilityUpdate,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: DispatchService = Depends(get_dispatch_service),
) -> dict:  # type: ignore
    """Update driver online/offline status."""
    try:
        await service.update_driver_availability(
            driver_id=update.driver_id,
            is_available=update.is_available,
            lat=update.latitude,
            lon=update.longitude,
        )
        return {"status": "success", "message": "Availability updated"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/decisions", status_code=status.HTTP_200_OK)
async def submit_dispatch_decision(
    decision: DispatchDecision,
    background_tasks: BackgroundTasks,
    current_user: dict[str, Any] = Depends(
        require_roles(Role.OPERATOR, Role.DRIVER, Role.PLATFORM_ADMIN)
    ),
    service: DispatchService = Depends(get_dispatch_service),
) -> dict:  # type: ignore
    """Submit a driver's decision (accept/reject) for an assignment offer."""
    try:
        background_tasks.add_task(
            service.handle_driver_decision, decision.attempt_id, decision.accepted
        )
        return {"status": "success", "message": "Decision received"}
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/{booking_id}/start", status_code=status.HTTP_202_ACCEPTED)
async def trigger_manual_dispatch(
    booking_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: DispatchService = Depends(get_dispatch_service),
) -> dict:  # type: ignore
    """Manually trigger the dispatch process for a booking."""
    background_tasks.add_task(service.start_dispatch, booking_id)
    return {"status": "success", "message": "Dispatch triggered"}
