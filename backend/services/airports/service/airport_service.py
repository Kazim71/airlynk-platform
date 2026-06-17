"""
AirLynk — Airport Service.
"""
import logging
from typing import Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.airports.repository.airport_repo import AirportRepository
from backend.services.airports.models.airport import Airport

logger = logging.getLogger(__name__)

class AirportService:
    def __init__(self, session: AsyncSession):
        self.repo = AirportRepository(session)

    async def list_airports(self) -> Sequence[Airport]:
        return await self.repo.get_all_active()

    async def search_airports(self, query: str) -> Sequence[Airport]:
        if not query or len(query) < 2:
            return []
        return await self.repo.search(query)

    async def get_airport(self, code: str) -> Airport:
        airport = await self.repo.get_by_code(code)
        if not airport:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Airport with code {code} not found."
            )
        return airport
