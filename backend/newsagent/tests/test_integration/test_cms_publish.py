import json

import httpx
import pytest
from httpx import ASGITransport

from newsagent.agents.publisher_agent import PublisherAgent
from newsagent.core.state import ArticleState
from newsagent.tools.cms_client import CMSClient


class FakeLLMPublisher:
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return "JUDUL: Dampak AI di Indonesia\n\nKONTEN:\nArtikel tentang dampak AI."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


async def _wp_app(scope, receive, send):
    assert scope["type"] == "http"
    assert scope["method"] == "POST"
    assert scope["path"] == "/wp-json/wp/v2/posts"

    body = b""
    more = True
    while more:
        msg = await receive()
        if msg["type"] == "http.request":
            body += msg.get("body", b"")
            more = msg.get("more_body", False)
        else:
            more = False

    data = json.loads(body)

    await send(
        {
            "type": "http.response.start",
            "status": 201,
            "headers": [(b"content-type", b"application/json")],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": json.dumps(
                {
                    "id": 999,
                    "title": {"rendered": data["title"]},
                    "status": data.get("status", "publish"),
                    "link": "https://example.com/artikel/999",
                }
            ).encode(),
        }
    )


@pytest.mark.asyncio
async def test_publisher_cms_end_to_end() -> None:
    transport = ASGITransport(app=_wp_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        cms = CMSClient(base_url="http://test", api_key="test-key", client=client)
        publisher = PublisherAgent(llm=FakeLLMPublisher(), cms=cms)

        state: ArticleState = {
            "article_id": "e2e-cms",
            "input_type": "topic",
            "raw_input": "Dampak AI di Indonesia",
            "rag_context": "",
            "draft": "Draft artikel.",
            "fact_check_report": {},
            "edited_draft": "Draf diedit.",
            "aggregated_article": "Artikel final tentang AI.",
            "credibility_score": 0.0,
            "status": "processing",
            "events": [],
        }

        result = await publisher.run(state)

        assert result["status"] == "published"
        assert result["published_url"] == "https://example.com/artikel/999"
        assert result["published_title"] == "Dampak AI di Indonesia"
        assert "Artikel tentang dampak AI" in result["published_body"]


@pytest.mark.asyncio
async def test_publisher_cms_handles_api_error() -> None:
    async def _error_app(scope, receive, send):
        await send(
            {
                "type": "http.response.start",
                "status": 500,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b'{"message":"Internal server error"}',
            }
        )

    transport = ASGITransport(app=_error_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        cms = CMSClient(base_url="http://test", api_key="test-key", client=client)
        publisher = PublisherAgent(llm=FakeLLMPublisher(), cms=cms)

        state: ArticleState = {
            "article_id": "e2e-cms-fail",
            "input_type": "topic",
            "raw_input": "Topik",
            "rag_context": "",
            "draft": "Draft.",
            "fact_check_report": {},
            "edited_draft": "",
            "aggregated_article": "",
            "credibility_score": 0.0,
            "status": "processing",
            "events": [],
        }

        result = await publisher.run(state)

        assert result["status"] == "failed"


@pytest.mark.asyncio
async def test_publisher_no_cms_still_publishes() -> None:
    publisher = PublisherAgent(llm=FakeLLMPublisher())

    state: ArticleState = {
        "article_id": "e2e-no-cms",
        "input_type": "topic",
        "raw_input": "Topik",
        "rag_context": "",
        "draft": "Draft artikel.",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }

    result = await publisher.run(state)

    assert result["status"] == "published"
    assert result["published_url"] is None
    assert result["published_title"] != ""
