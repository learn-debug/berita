from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from tenacity import retry, stop_after_attempt, wait_exponential

P = ParamSpec("P")
R = TypeVar("R")


def with_retry(max_attempts: int = 3, backoff: float = 2.0) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=backoff, min=1, max=30),
        )
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            return func(*args, **kwargs)

        return wrapper

    return decorator
