import asyncio
import logging
import os
from typing import Any

import asyncpg
from pgvector.asyncpg import register_vector

from newsagent.core.config import settings as app_settings

logger = logging.getLogger(__name__)

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")


class PostgresEngine:
    def __init__(self) -> None:
        self._pool_instance: asyncpg.Pool | None = None
        self._pool_loop = None
        self._schema_initialized = False

    async def pool(self) -> asyncpg.Pool:
        current_loop = asyncio.get_running_loop()
        if self._pool_instance is not None and (
            self._pool_loop is not current_loop or self._pool_loop.is_closed()
        ):
            self._pool_instance = None
            self._schema_initialized = False

        if self._pool_instance is None:
            dsn = app_settings.database_url.replace("+asyncpg", "")
            self._pool_instance = await asyncpg.create_pool(
                dsn,
                min_size=1,
                max_size=5,
            )
            self._pool_loop = current_loop
            async with self._pool_instance.acquire() as conn:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                await register_vector(conn)
                await self._init_schema(conn)
        return self._pool_instance

    async def _init_schema(self, conn: asyncpg.Connection) -> None:
        if self._schema_initialized:
            return
        try:
            schema_path = os.path.abspath(SCHEMA_PATH)
            if os.path.exists(schema_path):
                with open(schema_path) as f:
                    sql = f.read()
                await conn.execute(sql)
                # Ensure new columns and tables exist for in-memory mapping to postgres
                await conn.execute("ALTER TABLE articles ADD COLUMN IF NOT EXISTS article_id_str TEXT UNIQUE")
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS article_claims (
                        article_id_str TEXT NOT NULL,
                        revision_count INTEGER NOT NULL,
                        claimed_at TIMESTAMPTZ DEFAULT NOW(),
                        PRIMARY KEY (article_id_str, revision_count)
                    )
                """)
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS agent_costs (
                        id SERIAL PRIMARY KEY,
                        agent TEXT NOT NULL,
                        model TEXT NOT NULL,
                        input_tokens INTEGER NOT NULL,
                        output_tokens INTEGER NOT NULL,
                        cost REAL NOT NULL,
                        timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                """)
                # Seed default owner if no users exist
                owner_exists = await conn.fetchval("SELECT COUNT(*) FROM users")
                if owner_exists == 0 and app_settings.owner_email and app_settings.owner_password:
                    from newsagent.api.auth_utils import hash_password

                    pw_hash = hash_password(app_settings.owner_password)
                    await conn.execute(
                        "INSERT INTO users (email, password_hash, name, role) VALUES ($1, $2, $3, 'owner') ON CONFLICT (email) DO NOTHING",
                        app_settings.owner_email,
                        pw_hash,
                        app_settings.owner_name or app_settings.owner_email,
                    )
                    logger.info("[schema] seeded owner: %s", app_settings.owner_email)

                logger.info("[schema] initialized from %s", schema_path)
                self._schema_initialized = True
            else:
                logger.warning("[schema] not found at %s", schema_path)
        except Exception as e:
            logger.warning("[schema] init error (non-fatal): %s", e)

    async def execute(self, query: str, *args: Any) -> str:
        p = await self.pool()
        async with p.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args: Any) -> list[dict[str, Any]]:
        p = await self.pool()
        async with p.acquire() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(r) for r in rows]

    async def fetchrow(self, query: str, *args: Any) -> dict[str, Any] | None:
        p = await self.pool()
        async with p.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

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
