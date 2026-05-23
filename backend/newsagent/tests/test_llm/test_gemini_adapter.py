from unittest.mock import AsyncMock, MagicMock

import pytest

from newsagent.llm.gemini_adapter import GeminiAdapter


def test_lazy_init_does_not_crash() -> None:
    adapter = GeminiAdapter()
    assert not hasattr(adapter, "_client")


def test_model_name() -> None:
    adapter = GeminiAdapter()
    assert "gemini" in adapter.model_name()


@pytest.mark.asyncio
async def test_complete_returns_text() -> None:
    adapter = GeminiAdapter()
    mock_response = MagicMock()
    mock_response.text = "response text"
    mock_client = AsyncMock()
    mock_client.aio.models.generate_content.return_value = mock_response
    adapter._client = mock_client

    result = await adapter.complete("test prompt", system="test system")

    assert result == "response text"
    mock_client.aio.models.generate_content.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_returns_empty_when_none() -> None:
    adapter = GeminiAdapter()
    mock_response = MagicMock()
    mock_response.text = None
    mock_client = AsyncMock()
    mock_client.aio.models.generate_content.return_value = mock_response
    adapter._client = mock_client

    result = await adapter.complete("test prompt")

    assert result == ""


@pytest.mark.asyncio
async def test_complete_propagates_api_error() -> None:
    adapter = GeminiAdapter()
    mock_client = AsyncMock()
    mock_client.aio.models.generate_content.side_effect = RuntimeError("API error")
    adapter._client = mock_client

    with pytest.raises(RuntimeError, match="API error"):
        await adapter.complete("test prompt")


@pytest.mark.asyncio
async def test_complete_structured_returns_raw() -> None:
    adapter = GeminiAdapter()
    mock_response = MagicMock()
    mock_response.text = '{"key": "value"}'
    mock_client = AsyncMock()
    mock_client.aio.models.generate_content.return_value = mock_response
    adapter._client = mock_client

    result = await adapter.complete_structured("test prompt", {"type": "object"}, system="test system")

    assert result == {"raw": '{"key": "value"}'}
    mock_client.aio.models.generate_content.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_structured_propagates_error() -> None:
    adapter = GeminiAdapter()
    mock_client = AsyncMock()
    mock_client.aio.models.generate_content.side_effect = RuntimeError("API error")
    adapter._client = mock_client

    with pytest.raises(RuntimeError, match="API error"):
        await adapter.complete_structured("test", {"type": "object"}, system="test system")
