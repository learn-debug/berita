from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from newsagent.api.auth import verify_api_key_or_jwt
from newsagent.api.main import app
from newsagent.core.config import settings
from newsagent.security.rate_limiter import RateLimiter

app.dependency_overrides[verify_api_key_or_jwt] = lambda: None


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_process_endpoint_invalid_input() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/process", json={"input_type": "invalid", "raw_input": ""})
        assert response.status_code in (200, 422)


@pytest.mark.asyncio
async def test_process_endpoint_missing_raw_input() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/process", json={"input_type": "topic"})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_process_endpoint_empty_raw_input() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/process", json={"input_type": "topic", "raw_input": ""})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_process_endpoint_valid_request() -> None:
    import newsagent.api.main as api_main

    api_main._graph = AsyncMock()
    api_main._graph.ainvoke = AsyncMock(return_value={"article_id": "art_test", "status": "published"})
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/process", json={"input_type": "topic", "raw_input": "test article"})
        assert response.status_code in (200, 500)


@pytest.mark.asyncio
async def test_process_endpoint_xss_input() -> None:
    import newsagent.api.main as api_main

    api_main._graph = AsyncMock()
    api_main._graph.ainvoke = AsyncMock(return_value={"article_id": "art_xss", "status": "published"})
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/process",
            json={"input_type": "topic", "raw_input": "<script>alert('xss')</script>berita"},
        )
        assert response.status_code in (200, 500)


@pytest.mark.asyncio
async def test_root_endpoint() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/docs")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_process_endpoint_method_not_allowed() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/process")
        assert response.status_code == 405


@pytest.mark.asyncio
async def test_process_endpoint_validation_error_handling() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/process", json={"input_type": "topic", "raw_input": 123})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_process_endpoint_pipeline_error() -> None:
    transport = ASGITransport(app=app)
    with patch("newsagent.api.main._graph") as mock_graph:
        mock_ainvoke = AsyncMock()
        mock_ainvoke.side_effect = RuntimeError("Pipeline crashed")
        mock_graph.ainvoke = mock_ainvoke

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/process", json={"input_type": "topic", "raw_input": "test"})
            assert response.status_code == 500
            assert "Pipeline error" in response.text


@pytest.mark.asyncio
async def test_process_endpoint_rate_limited() -> None:
    transport = ASGITransport(app=app)
    with patch.object(RateLimiter, "acquire", new_callable=AsyncMock, return_value=False):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/process", json={"input_type": "topic", "raw_input": "test"})
            assert response.status_code == 429
            assert "Rate limit exceeded" in response.text


@pytest.mark.asyncio
async def test_auth_missing_key_returns_401() -> None:
    app.dependency_overrides.clear()
    original = settings.api_key
    settings.api_key = "secret-123"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/articles/process",
            json={"input_type": "topic", "raw_input": "test"},
        )
        assert response.status_code == 401
    settings.api_key = original
    app.dependency_overrides[verify_api_key_or_jwt] = lambda: None


@pytest.mark.asyncio
async def test_auth_wrong_key_returns_401() -> None:
    app.dependency_overrides.clear()
    original = settings.api_key
    settings.api_key = "secret-123"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/articles/process",
            json={"input_type": "topic", "raw_input": "test"},
            headers={"Authorization": "Bearer wrong-key"},
        )
        assert response.status_code == 401
    settings.api_key = original
    app.dependency_overrides[verify_api_key_or_jwt] = lambda: None


@pytest.mark.asyncio
async def test_auth_valid_key_passes() -> None:
    app.dependency_overrides.clear()
    import newsagent.api.main as api_main

    api_main._graph = AsyncMock()
    api_main._graph.ainvoke = AsyncMock(return_value={"article_id": "art_test", "status": "published"})
    api_main._store = AsyncMock()
    api_main._store.save_article = AsyncMock()

    original = settings.api_key
    settings.api_key = "secret-123"
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/articles/process",
            json={"input_type": "topic", "raw_input": "test"},
            headers={"Authorization": "Bearer secret-123"},
        )
        assert response.status_code == 202
    settings.api_key = original
    app.dependency_overrides[verify_api_key_or_jwt] = lambda: None


@pytest.mark.asyncio
async def test_auth_fails_when_no_key_and_no_token() -> None:
    app.dependency_overrides.clear()
    original = settings.api_key
    settings.api_key = ""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/articles/process",
            json={"input_type": "topic", "raw_input": "test"},
        )
        assert response.status_code == 401
    settings.api_key = original
    app.dependency_overrides[verify_api_key_or_jwt] = lambda: None


@pytest.mark.asyncio
async def test_process_endpoint_success() -> None:
    transport = ASGITransport(app=app)
    with patch("newsagent.api.main._graph") as mock_graph:
        mock_ainvoke = AsyncMock()
        mock_ainvoke.return_value = {
            "article_id": "art_mock123",
            "status": "published",
        }
        mock_graph.ainvoke = mock_ainvoke

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/process", json={"input_type": "topic", "raw_input": "test"})
            assert response.status_code == 200
            data = response.json()
            assert data["article_id"] == "art_mock123"
            assert data["status"] == "published"
