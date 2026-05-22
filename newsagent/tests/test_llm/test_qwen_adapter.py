from unittest.mock import AsyncMock, MagicMock

import pytest

from newsagent.llm.qwen_adapter import QwenAdapter


def test_lazy_init_does_not_crash() -> None:
    adapter = QwenAdapter()
    assert not hasattr(adapter, "_client")


def test_model_name() -> None:
    adapter = QwenAdapter()
    assert "qwen" in adapter.model_name()


@pytest.mark.asyncio
async def test_complete_returns_text() -> None:
    adapter = QwenAdapter()
    mock_choice = MagicMock()
    mock_choice.message.content = "response text"
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    adapter._client = mock_client

    result = await adapter.complete("test prompt", system="test system")

    assert result == "response text"
    mock_client.chat.completions.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_returns_empty_when_none() -> None:
    adapter = QwenAdapter()
    mock_choice = MagicMock()
    mock_choice.message.content = None
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    adapter._client = mock_client

    result = await adapter.complete("test prompt")

    assert result == ""


@pytest.mark.asyncio
async def test_complete_propagates_api_error() -> None:
    adapter = QwenAdapter()
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=RuntimeError("API error"))
    adapter._client = mock_client

    with pytest.raises(RuntimeError, match="API error"):
        await adapter.complete("test prompt")


@pytest.mark.asyncio
async def test_complete_structured_returns_raw() -> None:
    adapter = QwenAdapter()
    mock_choice = MagicMock()
    mock_choice.message.content = '{"key": "value"}'
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
    adapter._client = mock_client

    result = await adapter.complete_structured("test prompt", {"type": "object"}, system="test system")

    assert result == {"raw": '{"key": "value"}'}
    mock_client.chat.completions.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_structured_propagates_error() -> None:
    adapter = QwenAdapter()
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=RuntimeError("API error"))
    adapter._client = mock_client

    with pytest.raises(RuntimeError, match="API error"):
        await adapter.complete_structured("test", {"type": "object"}, system="test system")
