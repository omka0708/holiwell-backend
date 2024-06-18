from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from .config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?async_fallback=True"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


metadata = MetaData()


async def get_async_session() -> AsyncSession | None:
    async with async_session_maker() as session:
        yield session
