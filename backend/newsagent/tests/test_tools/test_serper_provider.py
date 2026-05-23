from unittest.mock import AsyncMock, MagicMock

import pytest

from newsagent.tools.serper_provider import SerperSearchProvider


@pytest.mark.asyncio
async def test_search_returns_documents() -> None:
    provider = SerperSearchProvider(api_key="test-key")

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "organic": [
            {"title": "Hasil 1", "snippet": "Ini konten hasil 1", "link": "https://example.com/1"},
            {"title": "Hasil 2", "snippet": "Ini konten hasil 2", "link": "https://example.com/2"},
        ]
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    provider._client = mock_client

    results = await provider.search("test query", max_results=2)

    assert len(results) == 2
    assert "Ini konten hasil 1" in results[0]
    assert "Ini konten hasil 2" in results[1]
    mock_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_handles_empty_results() -> None:
    provider = SerperSearchProvider(api_key="test-key")

    mock_response = MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    provider._client = mock_client

    results = await provider.search("test query")

    assert results == []


@pytest.mark.asyncio
async def test_search_handles_api_error() -> None:
    provider = SerperSearchProvider(api_key="test-key")

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = RuntimeError("API error")

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    provider._client = mock_client

    results = await provider.search("test query")

    assert results == []


@pytest.mark.asyncio
async def test_close_idempotent() -> None:
    provider = SerperSearchProvider(api_key="test-key")
    await provider.close()
    await provider.close()
