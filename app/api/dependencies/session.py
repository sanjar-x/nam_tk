from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio.session import AsyncSession
from ...core.database import async_session


async def get_session() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session() as session:
        yield session
