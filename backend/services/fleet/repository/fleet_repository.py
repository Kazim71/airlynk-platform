"""
AirLynk — Fleet Repository.
"""

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.fleet.models.fleet import Driver


class FleetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_driver_by_id(self, driver_id: UUID) -> Driver | None:
        """Mock method for getting driver until fleet domain is implemented."""
        # For dispatch test logic, assume the driver exists
        return Driver(id=driver_id, status="ACTIVE")
