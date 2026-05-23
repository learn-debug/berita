import pytest

from newsagent.resilience.retry_policy import with_retry


def test_with_retry_decorator_exists() -> None:
    assert callable(with_retry)


def test_with_retry_default_params() -> None:
    decorator = with_retry()
    assert callable(decorator)


def test_with_retry_custom_params() -> None:
    decorator = with_retry(max_attempts=5, backoff=3.0)
    assert callable(decorator)


@pytest.mark.asyncio
async def test_with_retry_retries_on_failure() -> None:
    call_count = 0

    @with_retry(max_attempts=3, backoff=0.1)
    async def flaky() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RuntimeError("transient error")
        return "success"

    result = await flaky()
    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_with_retry_exhausts_attempts() -> None:
    call_count = 0

    @with_retry(max_attempts=2, backoff=0.1)
    async def always_fails() -> str:
        nonlocal call_count
        call_count += 1
        raise RuntimeError("persistent error")

    with pytest.raises(RuntimeError, match="persistent error"):
        await always_fails()
    assert call_count == 2
