from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from src.config import settings
from typing import Annotated, TypeAlias
from fastapi import Depends


connect_args = {"check_same_thread": False}
engine = create_async_engine(settings.database_url, connect_args=connect_args)


async def get_session():
    async with AsyncSession(engine) as session:
        yield session


SessionDep: TypeAlias = Annotated[AsyncSession, Depends(get_session)]
