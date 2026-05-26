import asyncio
import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import Any

import redis.asyncio as aioredis

from newsagent.core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self, max_calls: int = 60, window: float = 60.0, use_redis: bool = True) -> None:
        self._max_calls = max_calls
        self._window = window
        self._use_redis = use_redis

        # Local fallback
        self._calls: list[float] = []
        self._lock = asyncio.Lock()

        self._redis: aioredis.Redis | None = None
        self._redis_attempted = False

    async def _ensure_redis(self) -> None:
        if not self._use_redis or self._redis_attempted:
            return
        self._redis_attempted = True

        if not settings.redis_url:
            return

        try:
            self._redis = aioredis.from_url(
                settings.redis_url,
                socket_connect_timeout=2.0,
                decode_responses=True,
            )
            await self._redis.ping()
            logger.info("[RateLimiter] Connected to Redis successfully.")
        except Exception as e:
            logger.warning(
                "[RateLimiter] Redis connection failed: %s. Falling back to local rate limiting.", e
            )
            self._redis = None

    def _prune_local(self) -> None:
        now = time.monotonic()
        self._calls = [t for t in self._calls if now - t < self._window]

    def _prune(self) -> None:
        self._prune_local()

    def _allow(self) -> bool:
        if self._window <= 0.0:
            return True
        return len(self._calls) < self._max_calls

    async def acquire(self) -> bool:
        await self._ensure_redis()

        if self._redis:
            now = time.time()
            key = "newsagent:rate_limit:global"
            try:
                async with self._redis.pipeline() as pipe:
                    await pipe.zremrangebyscore(key, "-inf", now - self._window)
                    await pipe.zcard(key)
                    await pipe.zadd(key, {str(now): now})
                    await pipe.expire(key, int(self._window) + 1)
                    results = await pipe.execute()

                    count = results[1]
                    if count >= self._max_calls:
                        # Revert the ZADD since we exceeded the limit
                        await self._redis.zrem(key, str(now))
                        return False
                    return True
            except Exception as e:
                logger.error("[RateLimiter] Redis error: %s, falling back to local", e)
                # Fallback to local on error

        # Local fallback
        async with self._lock:
            self._prune_local()
            if not self._allow():
                return False
            self._calls.append(time.monotonic())
            return True

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not await self.acquire():
                raise RuntimeError("Rate limit exceeded")
            return await func(*args, **kwargs)

        return wrapper
