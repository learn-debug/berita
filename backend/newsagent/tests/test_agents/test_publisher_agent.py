import pytest

from newsagent.agents.publisher_agent import PublisherAgent
from newsagent.core.state import ArticleState


class FakeLLM:
    async def complete(self, prompt: str, system: str | None = None) -> str:
        return "JUDUL: Artikel Test\n\nKONTEN: Ini adalah artikel yang siap publikasi."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


class FakeLLMNoTitle:
    async def complete(self, prompt: str, system: str | None = None) -> str:
        return "Ini adalah artikel tanpa judul."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


BASE: ArticleState = {
    "article_id": "test-456",
    "input_type": "topic",
    "raw_input": "Topik test",
    "rag_context": "",
    "draft": "Ini adalah draft artikel.",
    "fact_check_report": {},
    "edited_draft": "",
    "aggregated_article": "",
    "credibility_score": 0.8,
    "status": "processing",
    "events": [],
}


@pytest.mark.asyncio
async def test_publisher_agent_sets_status_published() -> None:
    llm = FakeLLM()
    agent = PublisherAgent(llm=llm)

    result = await agent.run({**BASE})

    assert result["status"] == "published"
    assert result["published_title"] == "Artikel Test"
    assert "siap publikasi" in result["published_body"]
    assert len(result["events"]) == 1
    assert result["events"][0]["agent"] == "PublisherAgent"


@pytest.mark.asyncio
async def test_publisher_agent_uses_aggregated_first() -> None:
    llm = FakeLLM()
    agent = PublisherAgent(llm=llm)

    state: ArticleState = {
        **BASE,
        "draft": "Draft lama",
        "edited_draft": "Draf diedit",
        "aggregated_article": "Artikel hasil agregasi final.",
    }
    result = await agent.run(state)

    assert result["status"] == "published"


@pytest.mark.asyncio
async def test_publisher_agent_uses_edited_draft_when_no_aggregated() -> None:
    llm = FakeLLM()
    agent = PublisherAgent(llm=llm)

    state: ArticleState = {
        **BASE,
        "draft": "Draft lama",
        "edited_draft": "Draf yang diedit.",
        "aggregated_article": "",
    }
    result = await agent.run(state)

    assert result["status"] == "published"


@pytest.mark.asyncio
async def test_publisher_agent_fallback_to_draft() -> None:
    llm = FakeLLM()
    agent = PublisherAgent(llm=llm)

    state: ArticleState = {
        **BASE,
        "draft": "Hanya draft saja.",
        "edited_draft": "",
        "aggregated_article": "",
    }
    result = await agent.run(state)

    assert result["status"] == "published"


@pytest.mark.asyncio
async def test_publisher_agent_handles_llm_error() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None) -> str:
            raise RuntimeError("API error")

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    agent = PublisherAgent(llm=llm)

    state: ArticleState = {
        **BASE,
        "aggregated_article": "Artikel final.",
    }
    result = await agent.run(state)

    assert result["status"] == "failed"
    assert result["events"][0]["action"] == "publish_failed"


@pytest.mark.asyncio
async def test_publisher_agent_fallback_title_when_no_match() -> None:
    llm = FakeLLMNoTitle()
    agent = PublisherAgent(llm=llm)

    state: ArticleState = {
        **BASE,
        "aggregated_article": "Konten artikel tanpa format judul.",
    }
    result = await agent.run(state)

    assert result["status"] == "published"
    assert "test-456" in result["published_title"]


@pytest.mark.asyncio
async def test_publisher_agent_parses_title_and_body() -> None:
    llm = FakeLLM()
    agent = PublisherAgent(llm=llm)

    result = await agent.run({**BASE})

    assert result["published_title"] == "Artikel Test"
    assert result["published_body"] == "Ini adalah artikel yang siap publikasi."


@pytest.mark.asyncio
async def test_publisher_agent_cms_success() -> None:
    from unittest.mock import AsyncMock

    llm = FakeLLM()
    mock_cms = AsyncMock()
    mock_cms.publish.return_value = {"id": "123", "link": "https://cms.test/artikel/123"}
    agent = PublisherAgent(llm=llm, cms=mock_cms)

    result = await agent.run({**BASE})

    assert result["status"] == "published"
    assert result["published_url"] == "https://cms.test/artikel/123"
    mock_cms.publish.assert_awaited_once_with("Artikel Test", "Ini adalah artikel yang siap publikasi.")


@pytest.mark.asyncio
async def test_publisher_agent_cms_failure() -> None:
    from unittest.mock import AsyncMock

    llm = FakeLLM()
    mock_cms = AsyncMock()
    mock_cms.publish.side_effect = RuntimeError("CMS down")
    agent = PublisherAgent(llm=llm, cms=mock_cms)

    result = await agent.run({**BASE})

    assert result["status"] == "failed"
    assert result["events"][0]["action"] == "publish_failed"
