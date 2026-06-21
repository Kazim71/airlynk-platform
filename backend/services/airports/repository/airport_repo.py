"""
AirLynk — Airport Repository.
"""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.services.airports.models.airport import Airport


class AirportRepository:
    """Data access for Airports."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_active(self) -> Sequence[Airport]:
        stmt = select(Airport).where(Airport.is_active == True).order_by(Airport.city)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_code(self, code: str) -> Airport | None:
        stmt = select(Airport).where(Airport.code == code.upper(), Airport.is_active == True)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(self, query: str) -> Sequence[Airport]:
        search_term = f"%{query}%"
        stmt = (
            select(Airport)
            .where(
                Airport.is_active == True,
                (Airport.code.ilike(search_term))
                | (Airport.city.ilike(search_term))
                | (Airport.name.ilike(search_term)),
            )
            .order_by(Airport.city)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
