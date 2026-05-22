from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R", bound=Awaitable[Any])


def with_fallback(
    fallback: Callable[..., Any] | None = None, default: Any = None
) -> Callable[[Callable[P, R]], Callable[P, Coroutine[Any, Any, Any]]]:
    def decorator(func: Callable[P, R]) -> Callable[P, Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception:
                if fallback is not None:
                    return await fallback(*args, **kwargs)
                return default

        return wrapper

    return decorator
