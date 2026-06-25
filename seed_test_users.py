import asyncio
import time
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from backend.shared.config.settings import get_settings
from backend.services.auth.models.user import User, Role
from backend.shared.security.password import hash_password

USERS = [
    {
        "role": "operator",
        "email": "operator_test@example.com",
        "password": "Test@123456"
    },
    {
        "role": "customer",
        "email": "customer_test@example.com",
        "password": "Test@123456"
    },
    {
        "role": "driver",
        "email": "driver_test@example.com",
        "password": "Test@123456"
    }
]

async def seed_users():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Wait for DB to be ready
    for _ in range(10):
        try:
            async with engine.begin() as conn:
                break
        except Exception:
            print("Waiting for database...")
            time.sleep(1)

    async with async_session() as session:
        for user_data in USERS:
            # Check if role exists
            result = await session.execute(select(Role).where(Role.name == user_data["role"]))
            role = result.scalars().first()
            if not role:
                role = Role(name=user_data["role"])
                session.add(role)
                await session.flush()
            
            # Check if user exists
            result = await session.execute(select(User).where(User.email == user_data["email"]))
            user = result.scalars().first()
            if not user:
                user = User(
                    email=user_data["email"],
                    hashed_password=hash_password(user_data["password"]),
                    role_id=role.id,
                    is_active=True
                )
                session.add(user)
                await session.commit()
                print(f"Successfully registered {user_data['email']} as {user_data['role']}")
            else:
                # Update role if incorrect
                if user.role_id != role.id:
                    user.role_id = role.id
                    session.add(user)
                    await session.commit()
                    print(f"Updated role for {user_data['email']} to {user_data['role']}")
                else:
                    print(f"User {user_data['email']} already exists with correct role.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(seed_users())
