from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

P = ParamSpec("P")
R = TypeVar("R", bound=Awaitable[Any])


def _is_rate_limited(e: BaseException) -> bool:
    msg = str(e).lower()
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
    max_attempts: int = 5, backoff: float = 2.0
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=backoff, min=2, max=60),
            retry=retry_if_exception(_is_rate_limited),
            reraise=True,
        )
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            return await func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
