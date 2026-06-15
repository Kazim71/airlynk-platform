"""
AirLynk — Dispatch Repository.
"""

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.dispatch.models.dispatch import (
    AttemptStatus,
    DispatchAttempt,
    DispatchRequest,
    DispatchStatus,
)


class DispatchRepository:
    """Repository for managing dispatch requests and attempts."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_dispatch_request(self, booking_id: UUID) -> DispatchRequest:
        """Create a new dispatch request for a booking."""
        request = DispatchRequest(booking_id=booking_id, status=DispatchStatus.PENDING)
        self.session.add(request)
        await self.session.flush()
        return request

    async def get_dispatch_request(self, request_id: UUID) -> DispatchRequest | None:
        """Retrieve a dispatch request by ID."""
        stmt = (
            select(DispatchRequest)
            .where(DispatchRequest.id == request_id)
            .options(selectinload(DispatchRequest.attempts))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_dispatch_request_by_booking(self, booking_id: UUID) -> DispatchRequest | None:
        """Retrieve a dispatch request by booking ID."""
        stmt = (
            select(DispatchRequest)
            .where(DispatchRequest.booking_id == booking_id)
            .options(selectinload(DispatchRequest.attempts))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_dispatch_status(
        self, request_id: UUID, status: DispatchStatus, increment_retry: bool = False
    ) -> DispatchRequest | None:
        """Update the status of a dispatch request."""
        stmt = (
            update(DispatchRequest)
            .where(DispatchRequest.id == request_id)
            .values(
                status=status,
                retry_count=DispatchRequest.retry_count + (1 if increment_retry else 0),
            )
            .returning(DispatchRequest)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()

    async def create_dispatch_attempt(self, request_id: UUID, driver_id: UUID) -> DispatchAttempt:
        """Record an attempt to ping a driver."""
        attempt = DispatchAttempt(
            dispatch_request_id=request_id,
            driver_id=driver_id,
            status=AttemptStatus.OFFERED,
        )
        self.session.add(attempt)
        await self.session.flush()
        return attempt

    async def update_attempt_status(
        self, attempt_id: UUID, status: AttemptStatus
    ) -> DispatchAttempt | None:
        """Update the status of an individual ping attempt."""
        stmt = (
            update(DispatchAttempt)
            .where(DispatchAttempt.id == attempt_id)
            .values(status=status)
            .returning(DispatchAttempt)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()
