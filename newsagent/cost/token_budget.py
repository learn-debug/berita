from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R", bound=Awaitable[Any])


class TokenBudgetExceededError(Exception):
    pass


def with_budget(
    max_tokens: int = 4000,
) -> Callable[[Callable[P, R]], Callable[P, Coroutine[Any, Any, Any]]]:
    def decorator(func: Callable[P, R]) -> Callable[P, Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            result = await func(*args, **kwargs)
            if isinstance(result, str) and len(result) > max_tokens * 4:
                raise TokenBudgetExceededError(f"Output exceeds budget of {max_tokens} tokens")
            return result

        return wrapper

    return decorator
