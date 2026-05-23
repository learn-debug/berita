from unittest.mock import AsyncMock, MagicMock

import pytest

from newsagent.tools.web_search import WebSearchTool


@pytest.mark.asyncio
async def test_fetch_page_invalid_url() -> None:
    tool = WebSearchTool()
    with pytest.raises(Exception):
        await tool.fetch_page("not-a-valid-url")
    await tool.close()


@pytest.mark.asyncio
async def test_close_idempotent() -> None:
    tool = WebSearchTool()
    await tool.close()
    await tool.close()


@pytest.mark.asyncio
async def test_fetch_page_strips_html_tags() -> None:
    tool = WebSearchTool()

    mock_response = MagicMock()
    mock_response.text = """
    <html><body>
    <script>alert('xss')</script>
    <nav>Menu</nav>
    <footer>Footer</footer>
    <div class="content">Ini adalah konten utama artikel.</div>
    </body></html>
    """
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response

    tool._client = mock_client

    result = await tool.fetch_page("https://example.com/article")

    assert "script" not in result
    assert "nav" not in result or "Menu" not in result
    assert "footer" not in result
    assert "konten utama" in result
    mock_client.get.assert_awaited_once_with("https://example.com/article")


@pytest.mark.asyncio
async def test_search_constructs_url_and_fetches() -> None:
    tool = WebSearchTool()
    mock_response = MagicMock()
    mock_response.text = "<html><body>Hasil pencarian</body></html>"
    mock_response.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    tool._client = mock_client

    results = await tool.search("apa itu AI di Indonesia")

    assert len(results) > 0
    assert "Hasil pencarian" in results[0]
    mock_client.get.assert_awaited_once()
    await tool.close()


@pytest.mark.asyncio
async def test_search_returns_structured_results() -> None:
    tool = WebSearchTool()
    mock_response = MagicMock()
    mock_response.text = """
    <html><body>
    <div class="result__body">
      <a class="result__url" href="https://example.com/1">https://example.com/1</a>
      <span class="result__snippet">Ini adalah hasil pencarian pertama.</span>
    </div>
    <div class="result__body">
      <a class="result__url" href="https://example.com/2">https://example.com/2</a>
      <span class="result__snippet">Ini adalah hasil pencarian kedua.</span>
    </div>
    </body></html>
    """
    mock_response.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    tool._client = mock_client

    results = await tool.search("test query")

    assert len(results) == 2
    assert "hasil pencarian pertama" in results[0]
    assert "hasil pencarian kedua" in results[1]
    await tool.close()


@pytest.mark.asyncio
async def test_search_returns_empty_on_no_content() -> None:
    tool = WebSearchTool()
    mock_response = MagicMock()
    mock_response.text = "<html><body></body></html>"
    mock_response.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    tool._client = mock_client

    results = await tool.search("test query")

    assert results == []
    await tool.close()


@pytest.mark.asyncio
async def test_search_handles_http_error() -> None:
    tool = WebSearchTool()
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = RuntimeError("HTTP error")
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    tool._client = mock_client

    results = await tool.search("test query")

    assert results == []
    await tool.close()


@pytest.mark.asyncio
async def test_fetch_page_truncates_long_content() -> None:
    tool = WebSearchTool()

    mock_response = MagicMock()
    mock_response.text = f"<html><body>{'x' * 10000}</body></html>"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    tool._client = mock_client

    result = await tool.fetch_page("https://example.com/long")

    assert len(result) <= 5000
