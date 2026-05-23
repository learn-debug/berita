import pytest

from newsagent.resilience.fallback import with_fallback


async def _fallback(*args: str, **kwargs: str) -> str:
    return "fallback result"


@pytest.mark.asyncio
async def test_with_fallback_success() -> None:
    @with_fallback(fallback=_fallback)
    async def ok_func() -> str:
        return "original result"

    result = await ok_func()
    assert result == "original result"


@pytest.mark.asyncio
async def test_with_fallback_on_error() -> None:
    @with_fallback(fallback=_fallback)
    async def fail_func() -> str:
        raise ValueError("error")

    result = await fail_func()
    assert result == "fallback result"


@pytest.mark.asyncio
async def test_with_fallback_default_value() -> None:
    @with_fallback(default="default value")
    async def fail_func() -> str:
        raise ValueError("error")

    result = await fail_func()
    assert result == "default value"


@pytest.mark.asyncio
async def test_with_fallback_no_fallback() -> None:
    @with_fallback()
    async def fail_func() -> str:
        raise ValueError("error")

    result = await fail_func()
    assert result is None
