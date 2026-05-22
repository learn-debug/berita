from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from tenacity import retry, stop_after_attempt, wait_exponential

P = ParamSpec("P")
R = TypeVar("R")


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
