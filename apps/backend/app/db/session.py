from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(get_settings().database_url, echo=False)
    return _engine


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSession(get_engine(), expire_on_commit=False) as session:
        yield session
