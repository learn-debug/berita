import asyncio
import time
from collections.abc import Callable
from functools import wraps
from typing import Any


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0) -> None:
        self._failure_count = 0
        self._failure_threshold = failure_threshold
        self._reset_timeout = reset_timeout
        self._last_failure_time: float | None = None
        self._state = "closed"
        self._lock = asyncio.Lock()

    @property
    def state(self) -> str:
        return self._state

    def _try_half_open(self) -> bool:
        if self._state == "open" and self._last_failure_time is not None:
            if time.monotonic() - self._last_failure_time >= self._reset_timeout:
                self._state = "half-open"
                return True
        return False

    async def record_failure(self) -> None:
        async with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._failure_count >= self._failure_threshold:
                self._state = "open"

    async def record_success(self) -> None:
        async with self._lock:
            self._failure_count = 0
            self._state = "closed"

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if self._state == "open":
                self._try_half_open()
                if self._state == "open":
                    raise RuntimeError("Circuit breaker is open")
            try:
                result = await func(*args, **kwargs)
                await self.record_success()
                return result
            except Exception:
                await self.record_failure()
                raise

        return wrapper
