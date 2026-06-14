"""
AirLynk — Booking API Routes.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.booking.repository.booking_repository import BookingRepository
from backend.services.booking.schemas.booking import (
    AssignDriverRequest,
    BookingCreate,
    BookingResponse,
)
from backend.services.booking.service.booking_service import BookingService
from backend.shared.cache.redis_client import get_redis
from backend.shared.database.session import get_db_session
from backend.shared.middleware.rbac import Role, require_roles

router = APIRouter(prefix="/bookings", tags=["bookings"])


def get_booking_service(
    session: AsyncSession = Depends(get_db_session),
    redis: Redis = Depends(get_redis),  # type: ignore[type-arg]
) -> BookingService:
    repo = BookingRepository(session)
    return BookingService(repo, redis)


@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking(
    payload: BookingCreate,
    current_user: dict[str, Any] = Depends(require_roles(Role.CUSTOMER, Role.PLATFORM_ADMIN)),
    service: BookingService = Depends(get_booking_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    correlation_id = uuid.uuid4()
    return await service.create_booking(user_id, payload, correlation_id)


@router.get("", response_model=list[BookingResponse])
async def list_bookings(
    current_user: dict[str, Any] = Depends(
        require_roles(Role.CUSTOMER, Role.DRIVER, Role.OPERATOR, Role.PLATFORM_ADMIN)
    ),
    service: BookingService = Depends(get_booking_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    role = current_user.get("role")

    if role in [Role.CUSTOMER, Role.DRIVER]:
        return await service.get_customer_bookings(user_id)
    else:
        return await service.get_all_bookings()


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(
        require_roles(Role.CUSTOMER, Role.DRIVER, Role.OPERATOR, Role.PLATFORM_ADMIN)
    ),
    service: BookingService = Depends(get_booking_service),
) -> Any:
    return await service.get_booking(booking_id)


@router.patch("/{booking_id}/assign-driver", response_model=BookingResponse)
async def assign_driver(
    booking_id: uuid.UUID,
    payload: AssignDriverRequest,
    current_user: dict[str, Any] = Depends(require_roles(Role.OPERATOR, Role.PLATFORM_ADMIN)),
    service: BookingService = Depends(get_booking_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    correlation_id = uuid.uuid4()
    return await service.assign_driver(booking_id, payload, user_id, correlation_id)


@router.patch("/{booking_id}/start", response_model=BookingResponse)
async def start_trip(
    booking_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(require_roles(Role.DRIVER, Role.PLATFORM_ADMIN)),
    service: BookingService = Depends(get_booking_service),
) -> Any:
    driver_id = uuid.UUID(current_user["sub"])
    correlation_id = uuid.uuid4()
    return await service.start_trip(booking_id, driver_id, correlation_id)


@router.patch("/{booking_id}/complete", response_model=BookingResponse)
async def complete_trip(
    booking_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(require_roles(Role.DRIVER, Role.PLATFORM_ADMIN)),
    service: BookingService = Depends(get_booking_service),
) -> Any:
    driver_id = uuid.UUID(current_user["sub"])
    correlation_id = uuid.uuid4()
    return await service.complete_trip(booking_id, driver_id, correlation_id)


@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: uuid.UUID,
    current_user: dict[str, Any] = Depends(
        require_roles(Role.CUSTOMER, Role.OPERATOR, Role.PLATFORM_ADMIN)
    ),
    service: BookingService = Depends(get_booking_service),
) -> Any:
    user_id = uuid.UUID(current_user["sub"])
    correlation_id = uuid.uuid4()
    return await service.cancel_booking(booking_id, user_id, correlation_id)
