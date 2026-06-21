import asyncio

from backend.services.airports.models.airport import Airport
from backend.shared.database.session import close_db, get_db_session, init_db


async def seed() -> None:
    await init_db()
    async for session in get_db_session():
        airports = [
            Airport(
                code="DEL",
                name="Indira Gandhi International Airport",
                city="Delhi",
                latitude=28.5562,
                longitude=77.1000,
                timezone="Asia/Kolkata",
            ),
            Airport(
                code="BOM",
                name="Chhatrapati Shivaji Maharaj International Airport",
                city="Mumbai",
                latitude=19.0896,
                longitude=72.8656,
                timezone="Asia/Kolkata",
            ),
            Airport(
                code="BLR",
                name="Kempegowda International Airport",
                city="Bengaluru",
                latitude=13.1986,
                longitude=77.7066,
                timezone="Asia/Kolkata",
            ),
        ]
        session.add_all(airports)
        # commit is handled by get_db_session generator
        break
    await close_db()
    print("Airports seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
