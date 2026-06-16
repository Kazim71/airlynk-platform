import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from backend.shared.config.settings import get_settings
from backend.services.auth.models.user import User, Role
from backend.shared.security.password import hash_password
import uuid

async def seed_operator():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check if role exists
        result = await session.execute(select(Role).where(Role.name == "operator"))
        role = result.scalars().first()
        if not role:
            role = Role(name="operator")
            session.add(role)
            await session.flush()
        
        # Check if user exists
        result = await session.execute(select(User).where(User.email == "operator@airlynk.com"))
        user = result.scalars().first()
        if not user:
            user = User(
                email="operator@airlynk.com",
                hashed_password=hash_password("Admin123!"),
                role_id=role.id,
                is_active=True
            )
            session.add(user)
            await session.commit()
            print("Operator user created!")
        else:
            print("Operator user already exists!")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_operator())
