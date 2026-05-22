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

    result = await tool.search("apa itu AI di Indonesia")

    assert "Hasil pencarian" in result
    mock_client.get.assert_awaited_once_with(
        "https://duckduckgo.com/html/?q=apa+itu+AI+di+Indonesia"
    )
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
