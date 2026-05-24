from collections.abc import Awaitable, Callable, Coroutine
from functools import wraps
from typing import Any, ParamSpec

P = ParamSpec("P")


class TokenBudgetExceededError(Exception):
    pass


def with_budget(
    max_tokens: int = 4000,
) -> Callable[[Callable[P, Awaitable[Any]]], Callable[P, Coroutine[Any, Any, Any]]]:
    def decorator(func: Callable[P, Awaitable[Any]]) -> Callable[P, Coroutine[Any, Any, Any]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            result = await func(*args, **kwargs)
            text_to_check = ""
            if isinstance(result, str):
                text_to_check = result
            elif isinstance(result, dict):
                for key in ["draft", "edited_draft", "published_body", "aggregated_article"]:
                    if key in result and isinstance(result[key], str):
                        text_to_check = result[key]
                        break

            if text_to_check and len(text_to_check) > max_tokens * 4:
                raise TokenBudgetExceededError(f"Output exceeds budget of {max_tokens} tokens")
            return result

        return wrapper

    return decorator
