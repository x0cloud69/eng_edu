"""
Async DB 엔진, AsyncSession, 테넌트 컨텍스트 변수.
"""
from contextvars import ContextVar
from typing import AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import get_settings
from src.db.base import Base

_settings = get_settings()

engine = create_async_engine(
    _settings.database_url,
    echo=_settings.debug,
)
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

current_tenant_id: ContextVar[UUID | None] = ContextVar("current_tenant_id", default=None)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
