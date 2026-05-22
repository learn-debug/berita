import time
from collections.abc import Callable
from functools import wraps
from typing import Any


class RateLimiter:
    def __init__(self, max_calls: int = 10, window: float = 60.0) -> None:
        self._max_calls = max_calls
        self._window = window
        self._calls: list[float] = []

    def _prune(self) -> None:
        now = time.monotonic()
        self._calls = [t for t in self._calls if now - t < self._window]

    def _allow(self) -> bool:
        self._prune()
        return len(self._calls) < self._max_calls

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not self._allow():
                raise RuntimeError("Rate limit exceeded")
            self._calls.append(time.monotonic())
            return await func(*args, **kwargs)

        return wrapper
