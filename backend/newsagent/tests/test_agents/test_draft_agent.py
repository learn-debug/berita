import pytest

from newsagent.agents.draft_agent import DraftAgent
from newsagent.core.state import ArticleState


class FakeLLM:
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return "Judul: Test\n\nIni adalah artikel test."

    async def complete_structured(
        self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048
    ) -> dict:
        return {"output": "Judul: Test\n\nIni adalah artikel test."}

    def model_name(self) -> str:
        return "fake"


@pytest.mark.asyncio
async def test_draft_agent_returns_new_state() -> None:
    llm = FakeLLM()
    agent = DraftAgent(llm=llm)

    state: ArticleState = {
        "article_id": "test-123",
        "input_type": "topic",
        "raw_input": "Topik test",
        "rag_context": "Konteks dari RAG",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }

    result = await agent.run(state)

    assert result["draft"] != ""
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_draft_agent_fallback_on_error() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
            raise RuntimeError("API error")

        async def complete_structured(
            self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048
        ) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    agent = DraftAgent(llm=llm)

    state: ArticleState = {
        "article_id": "test-456",
        "input_type": "topic",
        "raw_input": "Topik fallback test",
        "rag_context": "Konteks RAG",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }

    result = await agent.run(state)

    assert result["draft"] == state["raw_input"]
    assert len(result["events"]) == 1
