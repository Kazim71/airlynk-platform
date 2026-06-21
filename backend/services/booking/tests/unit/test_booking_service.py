"""
AirLynk — Booking Service Unit Tests.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from backend.services.booking.models.booking import Booking, BookingStatus
from backend.services.booking.schemas.booking import AssignDriverRequest
from backend.services.booking.service.booking_service import BookingService
from backend.shared.exceptions.handlers import ConflictError


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def mock_redis() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def booking_service(mock_repo: AsyncMock, mock_redis: AsyncMock) -> BookingService:
    service = BookingService(mock_repo, mock_redis, db_session=AsyncMock())
    service.publisher = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_assign_driver_success(
    booking_service: BookingService, mock_repo: AsyncMock, mock_redis: AsyncMock
) -> None:
    booking_id = uuid.uuid4()
    operator_id = uuid.uuid4()
    correlation_id = uuid.uuid4()

    booking = Booking(id=booking_id, booking_status=BookingStatus.CREATED)

    mock_repo.get_booking_by_id.return_value = booking
    mock_repo.assign_driver.return_value = booking
    mock_redis.set.return_value = True  # lock acquired

    req = AssignDriverRequest(driver_id=uuid.uuid4(), vehicle_id=uuid.uuid4())

    result = await booking_service.assign_driver(booking_id, req, operator_id, correlation_id)

    assert result == booking
    mock_repo.assign_driver.assert_called_once()
    booking_service.publisher.publish_driver_assigned.assert_called_once()  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_assign_driver_lock_failed(
    booking_service: BookingService, mock_repo: AsyncMock, mock_redis: AsyncMock
) -> None:
    booking_id = uuid.uuid4()
    mock_redis.set.return_value = False  # lock failed

    req = AssignDriverRequest(driver_id=uuid.uuid4(), vehicle_id=uuid.uuid4())

    with pytest.raises(ConflictError, match="Booking is currently being modified"):
        await booking_service.assign_driver(booking_id, req, uuid.uuid4(), uuid.uuid4())


@pytest.mark.asyncio
async def test_start_trip_invalid_state(
    booking_service: BookingService, mock_repo: AsyncMock
) -> None:
    booking_id = uuid.uuid4()
    driver_id = uuid.uuid4()

    booking = Booking(
        id=booking_id, booking_status=BookingStatus.COMPLETED, assigned_driver_id=driver_id
    )
    mock_repo.get_booking_by_id.return_value = booking

    with pytest.raises(ConflictError, match="Cannot start trip from state"):
        await booking_service.start_trip(booking_id, driver_id, uuid.uuid4())
