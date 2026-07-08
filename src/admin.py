import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.models import User, Role
from src.auth.utils import get_password_hash
from src.database import engine
from src.config import settings

async def create_first_admin():
    async with AsyncSession(engine) as session:
        admin_user = User(
            email=settings.first_superuser_email,
            hashed_password=get_password_hash(settings.first_superuser_password),
            role=Role.admin
        )
        session.add(admin_user)
        await session.commit()

if __name__ == '__main__':
    asyncio.run(create_first_admin())