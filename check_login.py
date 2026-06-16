import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from backend.shared.config.settings import get_settings
from backend.services.auth.models.user import User, Role
from backend.shared.security.password import verify_password

async def check():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == "operator@airlynk.com"))
        user = result.scalars().first()
        if not user:
            print("User not found!")
        else:
            print("User found:", user.email)
            print("Is Active:", user.is_active)
            is_valid = verify_password("Admin123!", user.hashed_password)
            print("Password matches 'Admin123!':", is_valid)
            
            result = await session.execute(select(Role).where(Role.id == user.role_id))
            role = result.scalars().first()
            print("Role:", role.name if role else "None")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check())
