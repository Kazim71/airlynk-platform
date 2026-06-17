"""
AirLynk — Airport API Routes.
"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.shared.database.session import get_db_session
from backend.services.airports.schemas.airport import AirportResponse
from backend.services.airports.service.airport_service import AirportService

router = APIRouter(prefix="/airports", tags=["Airports"])

@router.get("", response_model=List[AirportResponse])
async def list_airports(session: AsyncSession = Depends(get_db_session)):
    """Get all active airports."""
    service = AirportService(session)
    return await service.list_airports()

@router.get("/search", response_model=List[AirportResponse])
async def search_airports(
    q: str = Query(..., min_length=2, description="Search query for code, city, or name"),
    session: AsyncSession = Depends(get_db_session)
):
    """Search for airports by query."""
    service = AirportService(session)
    return await service.search_airports(q)

@router.get("/{code}", response_model=AirportResponse)
async def get_airport(code: str, session: AsyncSession = Depends(get_db_session)):
    """Get airport by specific IATA code."""
    service = AirportService(session)
    return await service.get_airport(code)
