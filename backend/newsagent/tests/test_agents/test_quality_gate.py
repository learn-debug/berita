import pytest

from newsagent.agents.quality_gate import QualityGateAgent
from newsagent.core.state import ArticleState


class FakeLLM:
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return ""

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
        return {
            "fact_accuracy": 0.85,
            "narrative_consistency": 0.90,
            "conflict_resolution": 0.75,
            "source_quality": 0.80,
        }

    def model_name(self) -> str:
        return "fake"


BASE_STATE: ArticleState = {
    "article_id": "qg-test",
    "input_type": "topic",
    "raw_input": "Test",
    "rag_context": "",
    "draft": "Draft artikel.",
    "fact_check_report": {"claims": "test claim", "verdict": "SUPPORTED"},
    "edited_draft": "",
    "aggregated_article": "",
    "credibility_score": 0.0,
    "status": "processing",
    "events": [],
}


@pytest.mark.asyncio
async def test_quality_gate_auto_publish_high_score() -> None:
    llm = FakeLLM()
    agent = QualityGateAgent(llm=llm)

    result = await agent.run({**BASE_STATE})

    assert result["credibility_score"] > 0.75
    assert result["status"] == "processing"
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_quality_gate_editor_review() -> None:
    class MediumScoreLLM:
        async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
            return ""

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
            return {
                "fact_accuracy": 0.70,
                "narrative_consistency": 0.65,
                "conflict_resolution": 0.60,
                "source_quality": 0.55,
            }

        def model_name(self) -> str:
            return "fake"

    llm = MediumScoreLLM()
    agent = QualityGateAgent(llm=llm)

    result = await agent.run({**BASE_STATE})

    score = result["credibility_score"]
    assert 0.60 <= score <= 0.68
    assert result["status"] == "review"


@pytest.mark.asyncio
async def test_quality_gate_full_revision() -> None:
    class VeryLowScoreLLM:
        async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
            return ""

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
            return {
                "fact_accuracy": 0.20,
                "narrative_consistency": 0.30,
                "conflict_resolution": 0.10,
                "source_quality": 0.00,
            }

        def model_name(self) -> str:
            return "fake"

    llm = VeryLowScoreLLM()
    agent = QualityGateAgent(llm=llm)

    result = await agent.run({**BASE_STATE})

    assert 0.15 <= result["credibility_score"] <= 0.25
    assert result["status"] == "revision"


@pytest.mark.asyncio
async def test_quality_gate_score_at_auto_publish_boundary() -> None:
    class BoundaryLLM:
        async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
            return ""

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
            return {
                "fact_accuracy": 0.875,
                "narrative_consistency": 0.875,
                "conflict_resolution": 0.875,
                "source_quality": 0.875,
            }

        def model_name(self) -> str:
            return "fake"

    llm = BoundaryLLM()
    agent = QualityGateAgent(llm=llm)

    result = await agent.run({**BASE_STATE})
    assert result["credibility_score"] >= 0.87
    assert result["status"] == "processing"


@pytest.mark.asyncio
async def test_quality_gate_score_at_full_revision_boundary() -> None:
    class BoundaryLLM:
        async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
            return ""

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
            return {
                "fact_accuracy": 0.2,
                "narrative_consistency": 0.2,
                "conflict_resolution": 0.2,
                "source_quality": 0.2,
            }

        def model_name(self) -> str:
            return "fake"

    llm = BoundaryLLM()
    agent = QualityGateAgent(llm=llm)

    result = await agent.run({**BASE_STATE})
    assert result["credibility_score"] == 0.2
    assert result["status"] == "revision"


@pytest.mark.asyncio
async def test_quality_gate_fallback_on_error() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
            raise RuntimeError("API error")

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    agent = QualityGateAgent(llm=llm)

    result = await agent.run({**BASE_STATE})

    assert result["credibility_score"] == 0.0
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_quality_gate_uses_aggregated_article_first() -> None:
    llm = FakeLLM()
    agent = QualityGateAgent(llm=llm)

    state: ArticleState = {
        **BASE_STATE,
        "aggregated_article": "Artikel hasil agregasi.",
        "edited_draft": "Draf edited.",
    }
    result = await agent.run(state)

    assert result["credibility_score"] > 0.0
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_quality_gate_uses_edited_draft_when_no_aggregated() -> None:
    llm = FakeLLM()
    agent = QualityGateAgent(llm=llm)

    state: ArticleState = {
        **BASE_STATE,
        "aggregated_article": "",
        "edited_draft": "Draf yang sudah diedit.",
    }
    result = await agent.run(state)

    assert result["credibility_score"] > 0.0


def test_system_prompt_content() -> None:
    llm = FakeLLM()
    agent = QualityGateAgent(llm=llm)
    prompt = agent._system_prompt()
    assert "fact_accuracy" in prompt
    assert "narrative_consistency" in prompt
    assert "conflict_resolution" in prompt
    assert "source_quality" in prompt
    assert "0.0" in prompt
