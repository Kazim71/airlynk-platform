import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from backend.shared.config.settings import get_settings
from backend.services.airports.models.airport import Airport

airports_data = [
    {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "Delhi", "state": "Delhi", "latitude": 28.5562, "longitude": 77.1000, "timezone": "Asia/Kolkata"},
    {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai", "state": "Maharashtra", "latitude": 19.0896, "longitude": 72.8656, "timezone": "Asia/Kolkata"},
    {"code": "BLR", "name": "Kempegowda International Airport", "city": "Bengaluru", "state": "Karnataka", "latitude": 13.1986, "longitude": 77.7066, "timezone": "Asia/Kolkata"},
    {"code": "HYD", "name": "Rajiv Gandhi International Airport", "city": "Hyderabad", "state": "Telangana", "latitude": 17.2403, "longitude": 78.4294, "timezone": "Asia/Kolkata"},
    {"code": "MAA", "name": "Chennai International Airport", "city": "Chennai", "state": "Tamil Nadu", "latitude": 12.9941, "longitude": 80.1709, "timezone": "Asia/Kolkata"},
    {"code": "CCU", "name": "Netaji Subhas Chandra Bose International Airport", "city": "Kolkata", "state": "West Bengal", "latitude": 22.6520, "longitude": 88.4463, "timezone": "Asia/Kolkata"},
    {"code": "GOI", "name": "Dabolim Airport", "city": "Goa", "state": "Goa", "latitude": 15.3808, "longitude": 73.8314, "timezone": "Asia/Kolkata"},
    {"code": "AMD", "name": "Sardar Vallabhbhai Patel International Airport", "city": "Ahmedabad", "state": "Gujarat", "latitude": 23.0734, "longitude": 72.6266, "timezone": "Asia/Kolkata"},
    {"code": "PNQ", "name": "Pune Airport", "city": "Pune", "state": "Maharashtra", "latitude": 18.5793, "longitude": 73.9089, "timezone": "Asia/Kolkata"},
    {"code": "COK", "name": "Cochin International Airport", "city": "Kochi", "state": "Kerala", "latitude": 10.1518, "longitude": 76.3930, "timezone": "Asia/Kolkata"}
]

async def seed_airports():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        for data in airports_data:
            result = await session.execute(select(Airport).where(Airport.code == data["code"]))
            airport = result.scalars().first()
            if not airport:
                # State is not in model, let's remove it if it's not present. Let's check model first.
                # Model has id, code, name, city, country, latitude, longitude, timezone, is_active.
                new_airport = Airport(
                    code=data["code"],
                    name=data["name"],
                    city=data["city"],
                    country="India",
                    latitude=data["latitude"],
                    longitude=data["longitude"],
                    timezone=data["timezone"],
                    is_active=True
                )
                session.add(new_airport)
                print(f"Added {data['code']}")
            else:
                print(f"{data['code']} already exists")
        
        await session.commit()
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_airports())
