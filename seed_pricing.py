import asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from backend.shared.config.settings import get_settings
from backend.services.pricing.models.pricing import PricingRule

async def seed_pricing():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    cities = ["Delhi", "Mumbai", "Bengaluru", "Hyderabad", "Chennai", "Kochi"]
    vehicle_types = {
        "sedan": {"base_fare": Decimal("100.00"), "per_km_rate": Decimal("15.00"), "per_minute_rate": Decimal("1.50"), "minimum_fare": Decimal("150.00"), "airport_fee": Decimal("100.00")},
        "suv": {"base_fare": Decimal("150.00"), "per_km_rate": Decimal("22.00"), "per_minute_rate": Decimal("2.00"), "minimum_fare": Decimal("220.00"), "airport_fee": Decimal("150.00")},
        "luxury": {"base_fare": Decimal("250.00"), "per_km_rate": Decimal("35.00"), "per_minute_rate": Decimal("3.00"), "minimum_fare": Decimal("350.00"), "airport_fee": Decimal("250.00")}
    }

    async with async_session() as session:
        for city in cities:
            for vt, rates in vehicle_types.items():
                # Check if rule exists
                stmt = select(PricingRule).where(
                    PricingRule.city == city,
                    PricingRule.vehicle_type == vt
                )
                result = await session.execute(stmt)
                rule = result.scalars().first()
                if not rule:
                    rule = PricingRule(
                        city=city,
                        vehicle_type=vt,
                        base_fare=rates["base_fare"],
                        per_km_rate=rates["per_km_rate"],
                        per_minute_rate=rates["per_minute_rate"],
                        minimum_fare=rates["minimum_fare"],
                        airport_fee=rates["airport_fee"],
                        waiting_charge_per_minute=Decimal("2.00"),
                        cancellation_fee=Decimal("50.00"),
                        surge_multiplier=Decimal("1.00"),
                        active=True
                    )
                    session.add(rule)
                    print(f"Created rule for {city} - {vt}")
        await session.commit()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_pricing())
