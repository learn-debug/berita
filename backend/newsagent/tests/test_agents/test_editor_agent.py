import pytest

from newsagent.agents.editor_agent import EditorAgent
from newsagent.core.state import ArticleState


class FakeLLM:
    async def complete(self, prompt: str, system: str | None = None) -> str:
        return "Ini adalah artikel yang sudah diedit dengan tata bahasa yang baik."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


BASE: ArticleState = {
    "article_id": "test-123",
    "input_type": "topic",
    "raw_input": "Topik test",
    "rag_context": "",
    "draft": "Ini adalah draf kasar.",
    "fact_check_report": {},
    "edited_draft": "",
    "aggregated_article": "",
    "credibility_score": 0.0,
    "status": "processing",
    "events": [],
}


@pytest.mark.asyncio
async def test_editor_agent_returns_edited_draft() -> None:
    llm = FakeLLM()
    agent = EditorAgent(llm=llm)

    result = await agent.run({**BASE})

    assert result["edited_draft"] != ""
    assert len(result["events"]) == 1
    assert result["events"][0]["agent"] == "EditorAgent"
    assert result["events"][0]["action"] == "edit_draft"


@pytest.mark.asyncio
async def test_editor_agent_fallback_on_error() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None) -> str:
            raise RuntimeError("API error")

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    agent = EditorAgent(llm=llm)

    result = await agent.run({**BASE})

    assert result["edited_draft"] == BASE["draft"]
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_editor_agent_with_empty_draft() -> None:
    llm = FakeLLM()
    agent = EditorAgent(llm=llm)

    state: ArticleState = {**BASE, "draft": ""}
    result = await agent.run(state)

    assert result["edited_draft"] != ""
    assert len(result["events"]) == 1


def test_editor_system_prompt() -> None:
    llm = FakeLLM()
    agent = EditorAgent(llm=llm)
    prompt = agent._system_prompt()
    assert "menyempurnakan bahasa" in prompt
    assert "ejaan" in prompt
    assert "mengubah fakta" in prompt
