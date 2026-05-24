import pytest

from newsagent.agents.aggregator import AggregatorAgent
from newsagent.core.state import ArticleState


class FakeLLM:
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return "Artikel final hasil debat dan konsensus."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


BASE: ArticleState = {
    "article_id": "test-123",
    "input_type": "topic",
    "raw_input": "Topik test",
    "rag_context": "",
    "draft": "Draf asli",
    "fact_check_report": {"claims": "klaim 1"},
    "edited_draft": "",
    "aggregated_article": "",
    "credibility_score": 0.0,
    "status": "processing",
    "events": [],
}


@pytest.mark.asyncio
async def test_aggregator_uses_edited_draft_first() -> None:
    llm = FakeLLM()
    agent = AggregatorAgent(llm=llm)

    state: ArticleState = {**BASE, "edited_draft": "Draf yang sudah diedit."}
    result = await agent.run(state)

    assert result["aggregated_article"] != ""
    assert len(result["events"]) == 1
    assert result["events"][0]["agent"] == "Aggregator"


@pytest.mark.asyncio
async def test_aggregator_falls_back_to_draft() -> None:
    llm = FakeLLM()
    agent = AggregatorAgent(llm=llm)

    state: ArticleState = {**BASE, "edited_draft": ""}
    result = await agent.run(state)

    assert result["aggregated_article"] != ""
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_aggregator_with_empty_fact_check() -> None:
    llm = FakeLLM()
    agent = AggregatorAgent(llm=llm)

    state: ArticleState = {**BASE, "fact_check_report": {}}
    result = await agent.run(state)

    assert result["aggregated_article"] != ""
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_aggregator_fallback_on_error() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
            raise RuntimeError("API error")

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    agent = AggregatorAgent(llm=llm)

    state: ArticleState = {**BASE, "edited_draft": "Draf diedit."}
    result = await agent.run(state)

    assert result["aggregated_article"] == state["edited_draft"]
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_aggregator_fallback_to_draft_when_no_edited() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
            raise RuntimeError("API error")

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    agent = AggregatorAgent(llm=llm)

    state: ArticleState = {**BASE, "edited_draft": ""}
    result = await agent.run(state)

    assert result["aggregated_article"] == state["draft"]
    assert len(result["events"]) == 1
