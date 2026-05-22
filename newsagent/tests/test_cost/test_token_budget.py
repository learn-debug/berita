import pytest

from newsagent.cost.token_budget import TokenBudgetExceededError, with_budget


@pytest.mark.asyncio
async def test_with_budget_within_limit() -> None:
    @with_budget(max_tokens=10)
    async def short_output() -> str:
        return "hello world"

    result = await short_output()
    assert result == "hello world"


@pytest.mark.asyncio
async def test_with_budget_exactly_at_limit() -> None:
    @with_budget(max_tokens=3)
    async def exactly_at_limit() -> str:
        return "a b c"

    result = await exactly_at_limit()
    assert result == "a b c"


@pytest.mark.asyncio
async def test_with_budget_exceeded() -> None:
    @with_budget(max_tokens=2)
    async def long_output() -> str:
        return "a b c d e f g"

    with pytest.raises(TokenBudgetExceededError):
        await long_output()


@pytest.mark.asyncio
async def test_with_budget_non_string_return() -> None:
    @with_budget(max_tokens=10)
    async def returns_dict() -> dict:
        return {"key": "value"}

    result = await returns_dict()
    assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_with_budget_empty_string() -> None:
    @with_budget(max_tokens=10)
    async def empty() -> str:
        return ""

    result = await empty()
    assert result == ""


@pytest.mark.asyncio
async def test_with_budget_single_long_word_exceeds() -> None:
    @with_budget(max_tokens=1)
    async def long_word() -> str:
        return "a" * 10000

    with pytest.raises(TokenBudgetExceededError):
        await long_word()
