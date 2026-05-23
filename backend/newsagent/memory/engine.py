import logging
from typing import Any

import asyncpg
from pgvector.asyncpg import register_vector

from newsagent.core.config import settings

logger = logging.getLogger(__name__)


class PostgresEngine:
    def __init__(self) -> None:
        self._pool_instance: asyncpg.Pool | None = None

    async def pool(self) -> asyncpg.Pool:
        if self._pool_instance is None:
            dsn = settings.database_url.replace("+asyncpg", "")
            self._pool_instance = await asyncpg.create_pool(
                dsn,
                min_size=1,
                max_size=5,
            )
            async with self._pool_instance.acquire() as conn:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                await register_vector(conn)
        return self._pool_instance

    async def execute(self, query: str, *args: Any) -> str:
        p = await self.pool()
        async with p.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        p = await self.pool()
        async with p.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> asyncpg.Record | None:
        p = await self.pool()
        async with p.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args: Any) -> Any:
        p = await self.pool()
        async with p.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def close(self) -> None:
        if self._pool_instance:
            await self._pool_instance.close()
            self._pool_instance = None


_engine: PostgresEngine | None = None


async def get_engine() -> PostgresEngine:
    global _engine
    if _engine is None:
        _engine = PostgresEngine()
    return _engine
