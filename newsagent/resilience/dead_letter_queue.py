import json
from typing import Any

from redis.asyncio import Redis

from newsagent.core.config import settings


class DeadLetterQueue:
    def __init__(self) -> None:
        self._redis: Redis | None = None

    async def _conn(self) -> Redis:
        if self._redis is None:
            self._redis = await Redis.from_url(settings.redis_url).initialize()
        return self._redis

    async def push(
        self,
        article_id: str,
        agent: str,
        error: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        redis = await self._conn()
        entry = {
            "article_id": article_id,
            "agent": agent,
            "error": error,
            "payload": payload,
        }
        await redis.lpush("dlq:articles", json.dumps(entry, default=str))

    async def pop(self) -> dict[str, Any] | None:
        redis = await self._conn()
        raw: bytes | None = await redis.rpop("dlq:articles")  # type: ignore[assignment]
        if raw is None:
            return None
        return json.loads(raw)
