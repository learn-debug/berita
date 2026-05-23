from unittest.mock import AsyncMock, patch

import pytest

from newsagent.tools.tavily_provider import TavilySearchProvider


@pytest.mark.asyncio
async def test_search_returns_documents() -> None:
    mock_client = AsyncMock()
    mock_client.search.return_value = {
        "results": [
            {
                "content": "Konten hasil 1",
                "url": "https://example.com/1",
            },
            {
                "raw_content": "Konten raw 2",
                "url": "https://example.com/2",
            },
        ]
    }

    with patch("newsagent.tools.tavily_provider.AsyncTavilyClient", return_value=mock_client):
        provider = TavilySearchProvider(api_key="test-key")
        results = await provider.search("test query", max_results=2)

    assert len(results) == 2
    assert "Konten hasil 1" in results[0]
    assert "Konten raw 2" in results[1]
    assert "example.com" in results[0]


@pytest.mark.asyncio
async def test_search_empty_results() -> None:
    mock_client = AsyncMock()
    mock_client.search.return_value = {"results": []}

    with patch("newsagent.tools.tavily_provider.AsyncTavilyClient", return_value=mock_client):
        provider = TavilySearchProvider(api_key="test-key")
        results = await provider.search("test query")

    assert results == []


@pytest.mark.asyncio
async def test_search_skips_empty_content() -> None:
    mock_client = AsyncMock()
    mock_client.search.return_value = {
        "results": [
            {"content": "", "raw_content": None, "url": "https://example.com/1"},
            {"content": "Ada konten", "url": "https://example.com/2"},
        ]
    }

    with patch("newsagent.tools.tavily_provider.AsyncTavilyClient", return_value=mock_client):
        provider = TavilySearchProvider(api_key="test-key")
        results = await provider.search("test query")

    assert len(results) == 1
    assert "Ada konten" in results[0]


@pytest.mark.asyncio
async def test_search_handles_api_error() -> None:
    mock_client = AsyncMock()
    mock_client.search.side_effect = RuntimeError("API error")

    with patch("newsagent.tools.tavily_provider.AsyncTavilyClient", return_value=mock_client):
        provider = TavilySearchProvider(api_key="test-key")
        results = await provider.search("test query")

    assert results == []


@pytest.mark.asyncio
async def test_close() -> None:
    mock_client = AsyncMock()

    with patch("newsagent.tools.tavily_provider.AsyncTavilyClient", return_value=mock_client):
        provider = TavilySearchProvider(api_key="test-key")
        await provider.close()

    mock_client.close.assert_awaited_once()
