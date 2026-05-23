from unittest.mock import AsyncMock, MagicMock

import pytest

from newsagent.tools.cms_client import CMSClient


def test_name_and_description() -> None:
    client = CMSClient(base_url="http://cms.test", api_key="test-key")
    assert client.name == "cms_client"
    assert "Publish" in client.description


@pytest.mark.asyncio
async def test_publish_invalid_url() -> None:
    client = CMSClient(base_url="http://localhost:99999", api_key="test")
    with pytest.raises(Exception):
        await client.publish("Title", "Content")
    await client.close()


@pytest.mark.asyncio
async def test_close_idempotent() -> None:
    client = CMSClient(base_url="http://localhost:99999", api_key="test")
    await client.close()
    await client.close()


@pytest.mark.asyncio
async def test_publish_success() -> None:
    client = CMSClient(base_url="http://cms.test", api_key="test-key")

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"id": 123, "status": "publish"}
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    client._client = mock_client

    result = await client.publish("Judul Artikel", "Konten artikel", status="publish")

    assert result == {"id": 123, "status": "publish"}
    mock_client.post.assert_awaited_once_with(
        "/wp-json/wp/v2/posts",
        json={"title": "Judul Artikel", "content": "Konten artikel", "status": "publish"},
    )


@pytest.mark.asyncio
async def test_publish_with_draft_status() -> None:
    client = CMSClient(base_url="http://cms.test", api_key="test-key")

    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"id": 456, "status": "draft"}
    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    client._client = mock_client

    result = await client.publish("Judul", "Konten", status="draft")

    assert result["status"] == "draft"
    mock_client.post.assert_awaited_once_with(
        "/wp-json/wp/v2/posts",
        json={"title": "Judul", "content": "Konten", "status": "draft"},
    )
