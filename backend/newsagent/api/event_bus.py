import asyncio
import contextlib
import json
import logging
from typing import Any

import redis.asyncio as aioredis

from newsagent.core.config import settings

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = {}
        self._redis: aioredis.Redis | None = None
        self._pubsub_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        self._redis_connect_task: asyncio.Task | None = None
        self._redis_attempted = False

    async def _ensure_redis(self) -> None:
        async with self._lock:
            if self._redis_attempted:
                return
            self._redis_attempted = True

            if not settings.redis_url:
                logger.info("[EventBus] Redis URL not configured. Using local in-memory EventBus.")
                return

            try:
                # Construct Redis client using standard async redis library
                dsn = settings.redis_url
                self._redis = aioredis.from_url(
                    dsn,
                    socket_connect_timeout=2.0,
                    decode_responses=True,
                )
                # Verify connection
                await self._redis.ping()
                logger.info("[EventBus] Connected to Redis Pub/Sub successfully.")

                # Start the background pub/sub pattern listener
                self._pubsub_task = asyncio.create_task(self._listen_redis_pubsub())
            except Exception as e:
                logger.warning(
                    "[EventBus] Redis connection failed: %s. Falling back to local in-memory EventBus.",
                    e,
                )
                self._redis = None

    async def _listen_redis_pubsub(self) -> None:
        if not self._redis:
            return
        pubsub = self._redis.pubsub()
        await pubsub.psubscribe("newsagent:article:*")
        logger.info("[EventBus] Subscribed to pattern newsagent:article:* in Redis")

        try:
            async for message in pubsub.listen():
                if message and message.get("type") == "pmessage":
                    channel = message.get("channel") or ""  # e.g., newsagent:article:abc123456
                    article_id = channel.split(":")[-1]
                    data_str = message.get("data") or ""

                    try:
                        event = json.loads(data_str)
                    except Exception:
                        continue

                    # Dispatch to all local queues for this article_id
                    async with self._lock:
                        queues = list(self._queues.get(article_id, []))

                    for q in queues:
                        await q.put(event)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error("[EventBus] Redis pubsub listener error: %s", e)
        finally:
            with contextlib.suppress(Exception):
                await pubsub.close()

    def subscribe(self, article_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._queues.setdefault(article_id, []).append(q)

        # Trigger Redis connection check asynchronously so we don't block
        self._redis_connect_task = asyncio.create_task(self._ensure_redis())

        return q

    def unsubscribe(self, article_id: str, q: asyncio.Queue) -> None:
        if article_id in self._queues:
            self._queues[article_id] = [x for x in self._queues[article_id] if x is not q]
            if not self._queues[article_id]:
                del self._queues[article_id]

    async def publish(self, article_id: str, event: dict[str, Any]) -> None:
        # 1. Deliver to local subscribers first
        queues = list(self._queues.get(article_id, []))
        for q in queues:
            await q.put(event)

        # 2. Trigger Redis check
        await self._ensure_redis()

        # 3. Publish to Redis channel so other worker processes receive it
        if self._redis:
            try:
                channel = f"newsagent:article:{article_id}"
                await self._redis.publish(channel, json.dumps(event))
            except Exception as e:
                logger.error("[EventBus] Failed to publish event to Redis: %s", e)
