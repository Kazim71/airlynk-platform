"""
AirLynk — Booking Repository.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.services.booking.models.booking import (
    Booking,
    BookingStatus,
    BookingStatusHistory,
    Trip,
    TripStatus,
)

if TYPE_CHECKING:
    from backend.services.booking.schemas.booking import BookingCreate


class BookingRepository:
    """Encapsulates data access for Booking, Trip, and History."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_booking(
        self, customer_id: uuid.UUID, data: BookingCreate, estimated_price: float
    ) -> Booking:
        """Create a new booking in CREATED state."""
        booking = Booking(
            customer_id=customer_id,
            pickup_location=data.pickup_location,
            dropoff_location=data.dropoff_location,
            scheduled_time=data.scheduled_time,
            passenger_count=data.passenger_count,
            estimated_price=estimated_price,
            booking_status=BookingStatus.CREATED,
        )
        self.session.add(booking)
        await self.session.flush()

        # Add initial status history
        history = BookingStatusHistory(
            booking_id=booking.id,
            old_status=None,
            new_status=BookingStatus.CREATED.value,
            changed_by=customer_id,
        )
        self.session.add(history)
        await self.session.commit()

        # Reload with relationships to prevent MissingGreenlet during serialization
        stmt = (
            select(Booking)
            .options(selectinload(Booking.trip), selectinload(Booking.status_history))
            .where(Booking.id == booking.id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_booking_by_id(self, booking_id: uuid.UUID) -> Booking | None:
        """Fetch booking with its trip and status history."""
        stmt = (
            select(Booking)
            .options(selectinload(Booking.trip), selectinload(Booking.status_history))
            .where(Booking.id == booking_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_customer_bookings(
        self, customer_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> Sequence[Booking]:
        """Fetch bookings for a specific customer."""
        stmt = (
            select(Booking)
            .options(selectinload(Booking.trip))
            .where(Booking.customer_id == customer_id)
            .order_by(Booking.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_all_bookings(self, limit: int = 50, offset: int = 0) -> Sequence[Booking]:
        """Fetch all bookings (for operators/admins)."""
        stmt = (
            select(Booking)
            .options(selectinload(Booking.trip))
            .order_by(Booking.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_booking_status(
        self, booking: Booking, new_status: BookingStatus, changed_by: uuid.UUID
    ) -> Booking:
        """Update booking status and record in history within one transaction."""
        old_status = booking.booking_status
        booking.booking_status = new_status

        history = BookingStatusHistory(
            booking_id=booking.id,
            old_status=old_status.value,
            new_status=new_status.value,
            changed_by=changed_by,
        )
        self.session.add(history)
        await self.session.commit()
        await self.session.refresh(booking)
        return booking

    async def assign_driver(
        self, booking: Booking, driver_id: uuid.UUID, vehicle_id: uuid.UUID, changed_by: uuid.UUID
    ) -> Booking:
        """Assign driver to a booking and initialize the trip."""
        old_status = booking.booking_status
        booking.assigned_driver_id = driver_id
        booking.vehicle_id = vehicle_id
        booking.booking_status = BookingStatus.DRIVER_ASSIGNED

        history = BookingStatusHistory(
            booking_id=booking.id,
            old_status=old_status.value,
            new_status=BookingStatus.DRIVER_ASSIGNED.value,
            changed_by=changed_by,
        )
        self.session.add(history)

        trip = Trip(booking_id=booking.id, trip_status=TripStatus.PENDING)
        self.session.add(trip)

        await self.session.commit()
        await self.session.refresh(booking)
        return booking

    async def update_trip_status(
        self,
        trip: Trip,
        new_status: TripStatus,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> Trip:
        """Update the trip status and optional timestamps."""
        trip.trip_status = new_status
        if started_at:
            trip.started_at = started_at
        if completed_at:
            trip.completed_at = completed_at

        await self.session.commit()
        await self.session.refresh(trip)
        return trip
