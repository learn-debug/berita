import asyncio
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

P = ParamSpec("P")
R = TypeVar("R", bound=Awaitable[Any])

_provider_semaphores: dict[str, asyncio.Semaphore] = {}
_provider_last_call: dict[str, float] = {}
_provider_lock = asyncio.Lock()


class RateLimiter:
    def __init__(self, provider: str, max_concurrent: int = 1, min_interval: float = 1.5):
        self.provider = provider
        self.max_concurrent = max_concurrent
        self.min_interval = min_interval

    async def acquire(self) -> None:
        async with _provider_lock:
            if self.provider not in _provider_semaphores:
                _provider_semaphores[self.provider] = asyncio.Semaphore(self.max_concurrent)
                _provider_last_call[self.provider] = 0.0
            sem = _provider_semaphores[self.provider]
            last = _provider_last_call[self.provider]

        await sem.acquire()
        now = asyncio.get_event_loop().time()
        wait = self.min_interval - (now - last)
        if wait > 0:
            await asyncio.sleep(wait)
        async with _provider_lock:
            _provider_last_call[self.provider] = asyncio.get_event_loop().time()

    def release(self) -> None:
        _provider_semaphores[self.provider].release()


def _is_rate_limited(e: BaseException) -> bool:
    msg = str(e).lower()
    if "quota" in msg and ("exceeded" in msg or "exhausted" in msg):
        return False
    if "402" in msg and "payment" in msg:
        return False
    return "rate limit" in msg or "rate_limit" in msg or "429" in msg


def with_retry(max_attempts: int = 3, backoff: float = 2.0) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=backoff, min=1, max=30),
            reraise=True,
        )
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            return await func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def with_rate_limit_retry(
    max_attempts: int = 10, backoff: float = 5.0
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=backoff, min=5, max=120),
            retry=retry_if_exception(_is_rate_limited),
            reraise=True,
        )
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            return await func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
