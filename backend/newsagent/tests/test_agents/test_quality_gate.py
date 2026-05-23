import pytest

from newsagent.agents.quality_gate import QualityGateAgent
from newsagent.core.state import ArticleState


class FakeLLM:
    async def complete(self, prompt: str, system: str | None = None) -> str:
        return (
            "fact_accuracy: 0.85\n"
            "narrative_consistency: 0.90\n"
            "conflict_resolution: 0.75\n"
            "source_quality: 0.80"
        )

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
        return {"raw": "test"}

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
        async def complete(self, prompt: str, system: str | None = None) -> str:
            return (
                "fact_accuracy: 0.70\n"
                "narrative_consistency: 0.65\n"
                "conflict_resolution: 0.60\n"
                "source_quality: 0.55"
            )

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
            return {"raw": "test"}

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
        async def complete(self, prompt: str, system: str | None = None) -> str:
            return (
                "fact_accuracy: 0.20\n"
                "narrative_consistency: 0.30\n"
                "conflict_resolution: 0.10\n"
                "source_quality: 0.00"
            )

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
            return {"raw": "test"}

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
        async def complete(self, prompt: str, system: str | None = None) -> str:
            return (
                "fact_accuracy: 0.875\n"
                "narrative_consistency: 0.875\n"
                "conflict_resolution: 0.875\n"
                "source_quality: 0.875"
            )

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
            return {"raw": "test"}

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
        async def complete(self, prompt: str, system: str | None = None) -> str:
            return (
                "fact_accuracy: 0.2\n"
                "narrative_consistency: 0.2\n"
                "conflict_resolution: 0.2\n"
                "source_quality: 0.2"
            )

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
            return {"raw": "test"}

        def model_name(self) -> str:
            return "fake"

    llm = BoundaryLLM()
    agent = QualityGateAgent(llm=llm)

    result = await agent.run({**BASE_STATE})
    assert result["credibility_score"] == 0.2
    assert result["status"] == "revision"


def test_parse_scores_normal() -> None:
    llm = FakeLLM()
    agent = QualityGateAgent(llm=llm)

    text = "fact_accuracy: 0.75\nnarrative_consistency: 0.80\nconflict_resolution: 0.65\nsource_quality: 0.90"
    scores = agent._parse_scores(text)

    assert scores["fact_accuracy"] == 0.75
    assert scores["narrative_consistency"] == 0.80
    assert scores["conflict_resolution"] == 0.65
    assert scores["source_quality"] == 0.90


def test_parse_scores_clamps_values() -> None:
    llm = FakeLLM()
    agent = QualityGateAgent(llm=llm)

    text = "fact_accuracy: -0.5\nnarrative_consistency: 1.5\nconflict_resolution: 0.x\nsource_quality: abc"
    scores = agent._parse_scores(text)

    assert scores["fact_accuracy"] == 0.0
    assert scores["narrative_consistency"] == 1.0
    assert scores["conflict_resolution"] == 0.0
    assert scores["source_quality"] == 0.0


def test_parse_scores_empty() -> None:
    llm = FakeLLM()
    agent = QualityGateAgent(llm=llm)

    scores = agent._parse_scores("no scores here")
    assert scores == {
        "fact_accuracy": 0.0,
        "narrative_consistency": 0.0,
        "conflict_resolution": 0.0,
        "source_quality": 0.0,
    }


def test_parse_scores_case_insensitive() -> None:
    llm = FakeLLM()
    agent = QualityGateAgent(llm=llm)

    text = "FACT_ACCURACY: 0.90\nNarrative_Consistency: 0.80"
    scores = agent._parse_scores(text)

    assert scores["fact_accuracy"] == 0.90
    assert scores["narrative_consistency"] == 0.80


def test_parse_scores_tab_delimiter() -> None:
    llm = FakeLLM()
    agent = QualityGateAgent(llm=llm)

    text = "fact_accuracy:\t0.70\nnarrative_consistency:\t0.60"
    scores = agent._parse_scores(text)

    assert scores["fact_accuracy"] == 0.70
    assert scores["narrative_consistency"] == 0.60


@pytest.mark.asyncio
async def test_quality_gate_fallback_on_error() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None) -> str:
            raise RuntimeError("API error")

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
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
    assert "0.0-1.0" in prompt
