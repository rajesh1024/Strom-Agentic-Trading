from datetime import datetime
from typing import Any

from sqlalchemy import MetaData, DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from src.config import settings

class Base(DeclarativeBase):
    pass

metadata = Base.metadata

# Engine and session factory
engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
