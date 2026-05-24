from unittest.mock import AsyncMock, MagicMock

import pytest
from anthropic.types import TextBlock

from newsagent.llm.claude_adapter import ClaudeAdapter


def test_extract_text_with_text_block() -> None:
    adapter = ClaudeAdapter()
    content = [TextBlock(text="hello world", type="text")]
    assert adapter._extract_text(content) == "hello world"


def test_extract_text_with_mixed_blocks() -> None:
    adapter = ClaudeAdapter()

    class NonTextBlock:
        def __init__(self) -> None:
            self.type = "tool_use"

    content = [NonTextBlock(), TextBlock(text="text here", type="text")]
    assert adapter._extract_text(content) == "text here"


def test_extract_text_empty() -> None:
    adapter = ClaudeAdapter()
    assert adapter._extract_text([]) == ""


def test_model_name() -> None:
    adapter = ClaudeAdapter()
    assert "claude" in adapter.model_name()


@pytest.mark.asyncio
async def test_complete_returns_text() -> None:
    adapter = ClaudeAdapter()
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [TextBlock(text="response text", type="text")]
    mock_messages = AsyncMock()
    mock_messages.create.return_value = mock_response
    mock_client.messages = mock_messages
    adapter._client = mock_client

    result = await adapter.complete("test prompt", system="test system")

    assert result == "response text"
    mock_messages.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_propagates_api_error() -> None:
    adapter = ClaudeAdapter()
    mock_client = MagicMock()
    mock_messages = AsyncMock()
    mock_messages.create.side_effect = RuntimeError("API error")
    mock_client.messages = mock_messages
    adapter._client = mock_client

    with pytest.raises(RuntimeError, match="API error"):
        await adapter.complete("test prompt", system="test system")


@pytest.mark.asyncio
async def test_complete_structured_returns_raw() -> None:
    adapter = ClaudeAdapter()
    mock_client = MagicMock()

    mock_response = MagicMock()
    mock_response.content = [TextBlock(text='{"key": "value"}', type="text")]
    mock_messages = AsyncMock()
    mock_messages.create.return_value = mock_response
    mock_client.messages = mock_messages
    adapter._client = mock_client

    result = await adapter.complete_structured("test prompt", {"type": "object"}, system="test system")

    assert result == {"key": "value"}
    mock_messages.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_complete_structured_propagates_error() -> None:
    adapter = ClaudeAdapter()
    mock_client = MagicMock()
    mock_messages = AsyncMock()
    mock_messages.create.side_effect = RuntimeError("API error")
    mock_client.messages = mock_messages
    adapter._client = mock_client

    with pytest.raises(RuntimeError, match="API error"):
        await adapter.complete_structured("test", {"type": "object"}, system="test")
