import asyncio

from sqlalchemy import select

from backend.services.airports.models.airport import Airport
from backend.shared.database.session import close_db, get_db_session, init_db


async def seed() -> None:
    await init_db()
    async for session in get_db_session():
        # Clean existing airports first to avoid duplicates
        existing = await session.execute(select(Airport))
        for airport in existing.scalars().all():
            await session.delete(airport)
        await session.flush()

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
            Airport(
                code="HYD",
                name="Rajiv Gandhi International Airport",
                city="Hyderabad",
                latitude=17.2403,
                longitude=78.4294,
                timezone="Asia/Kolkata",
            ),
            Airport(
                code="MAA",
                name="Chennai International Airport",
                city="Chennai",
                latitude=12.9941,
                longitude=80.1709,
                timezone="Asia/Kolkata",
            ),
            Airport(
                code="CCU",
                name="Netaji Subhas Chandra Bose International Airport",
                city="Kolkata",
                latitude=22.6520,
                longitude=88.4467,
                timezone="Asia/Kolkata",
            ),
            Airport(
                code="GOI",
                name="Goa International Airport",
                city="Goa",
                latitude=15.3808,
                longitude=73.8313,
                timezone="Asia/Kolkata",
            ),
            Airport(
                code="AMD",
                name="Sardar Vallabhbhai Patel International Airport",
                city="Ahmedabad",
                latitude=23.0734,
                longitude=72.6261,
                timezone="Asia/Kolkata",
            ),
            Airport(
                code="PNQ",
                name="Pune Airport",
                city="Pune",
                latitude=18.5793,
                longitude=73.9089,
                timezone="Asia/Kolkata",
            ),
            Airport(
                code="COK",
                name="Cochin International Airport",
                city="Kochi",
                latitude=10.1518,
                longitude=76.3930,
                timezone="Asia/Kolkata",
            ),
        ]
        session.add_all(airports)
        await session.commit()
        break
    await close_db()
    print("Phase 1 Airports seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
