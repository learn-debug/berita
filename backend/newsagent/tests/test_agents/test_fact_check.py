import pytest

from newsagent.agents.fact_check.evidence_retrieval import EvidenceRetrievalAgent
from newsagent.agents.fact_check.input_ingestion import InputIngestionAgent
from newsagent.agents.fact_check.query_generation import QueryGenerationAgent
from newsagent.agents.fact_check.verdict_prediction import VerdictPredictionAgent
from newsagent.core.state import ArticleState


class FakeLLM:
    async def complete(self, prompt: str, system: str | None = None) -> str:
        return "Fake response for testing."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


BASE_FC: ArticleState = {
    "article_id": "fc-test",
    "input_type": "draft",
    "raw_input": "Test input",
    "rag_context": "",
    "draft": "Presiden mengatakan bahwa inflasi turun 5% tahun ini. PDB naik 3%.",
    "fact_check_report": {},
    "edited_draft": "Presiden mengatakan bahwa inflasi turun 5% tahun ini. PDB naik 3%.",
    "aggregated_article": "",
    "credibility_score": 0.0,
    "status": "processing",
    "events": [],
}


# =========== InputIngestion ===========


@pytest.mark.asyncio
async def test_input_ingestion_extracts_claims() -> None:
    llm = FakeLLM()
    agent = InputIngestionAgent(llm=llm)

    result = await agent.run({**BASE_FC})

    assert "claims" in result["fact_check_report"]
    assert result["fact_check_report"]["claims"] != ""
    assert len(result["events"]) == 1
    assert result["events"][0]["agent"] == "InputIngestion"


@pytest.mark.asyncio
async def test_input_ingestion_fallback_on_error() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None) -> str:
            raise RuntimeError("API error")

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    agent = InputIngestionAgent(llm=llm)

    result = await agent.run({**BASE_FC})

    assert result["fact_check_report"]["claims"] == ""
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_input_ingestion_uses_edited_draft_first() -> None:
    llm = FakeLLM()
    agent = InputIngestionAgent(llm=llm)

    state: ArticleState = {**BASE_FC, "edited_draft": "Edited version with claims."}
    result = await agent.run(state)

    assert "claims" in result["fact_check_report"]


@pytest.mark.asyncio
async def test_input_ingestion_falls_back_to_draft_when_no_edited() -> None:
    llm = FakeLLM()
    agent = InputIngestionAgent(llm=llm)

    state: ArticleState = {**BASE_FC, "edited_draft": ""}
    result = await agent.run(state)

    assert "claims" in result["fact_check_report"]


@pytest.mark.asyncio
async def test_input_ingestion_preserves_existing_fact_check_keys() -> None:
    llm = FakeLLM()
    agent = InputIngestionAgent(llm=llm)

    state: ArticleState = {**BASE_FC, "fact_check_report": {"existing_key": "should_survive"}}
    result = await agent.run(state)

    assert result["fact_check_report"]["existing_key"] == "should_survive"
    assert "claims" in result["fact_check_report"]


# =========== QueryGeneration ===========


@pytest.mark.asyncio
async def test_query_generation_creates_queries() -> None:
    llm = FakeLLM()
    agent = QueryGenerationAgent(llm=llm)

    state: ArticleState = {**BASE_FC, "fact_check_report": {"claims": "Inflasi turun 5%\nPDB naik 3%"}}
    result = await agent.run(state)

    assert "queries" in result["fact_check_report"]
    assert result["fact_check_report"]["queries"] != ""
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_query_generation_with_empty_claims() -> None:
    llm = FakeLLM()
    agent = QueryGenerationAgent(llm=llm)

    state: ArticleState = {**BASE_FC, "fact_check_report": {"claims": ""}}
    result = await agent.run(state)

    assert "queries" in result["fact_check_report"]


@pytest.mark.asyncio
async def test_query_generation_fallback_on_error() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None) -> str:
            raise RuntimeError("API error")

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    agent = QueryGenerationAgent(llm=llm)

    state: ArticleState = {**BASE_FC, "fact_check_report": {"claims": "test"}}
    result = await agent.run(state)

    assert result["fact_check_report"]["queries"] == ""
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_query_generation_preserves_existing_keys() -> None:
    llm = FakeLLM()
    agent = QueryGenerationAgent(llm=llm)

    state: ArticleState = {
        **BASE_FC,
        "fact_check_report": {"claims": "test claim", "existing_key": "should_survive"},
    }
    result = await agent.run(state)

    assert result["fact_check_report"]["existing_key"] == "should_survive"
    assert "queries" in result["fact_check_report"]


# =========== VerdictPrediction ===========


@pytest.mark.asyncio
async def test_verdict_prediction_uses_claims_and_evidence() -> None:
    llm = FakeLLM()
    agent = VerdictPredictionAgent(llm=llm)

    state: ArticleState = {
        **BASE_FC,
        "fact_check_report": {
            "claims": "Inflasi turun 5%",
            "evidence": "Data BPS menunjukkan inflasi 4.8%",
        },
    }
    result = await agent.run(state)

    assert "verdict" in result["fact_check_report"]
    assert result["fact_check_report"]["verdict"] != ""
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_verdict_prediction_with_empty_evidence() -> None:
    llm = FakeLLM()
    agent = VerdictPredictionAgent(llm=llm)

    state: ArticleState = {
        **BASE_FC,
        "fact_check_report": {"claims": "test claim", "evidence": ""},
    }
    result = await agent.run(state)

    assert "verdict" in result["fact_check_report"]


@pytest.mark.asyncio
async def test_verdict_prediction_fallback_on_error() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None) -> str:
            raise RuntimeError("API error")

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    agent = VerdictPredictionAgent(llm=llm)

    state: ArticleState = {**BASE_FC, "fact_check_report": {"claims": "test", "evidence": "test"}}
    result = await agent.run(state)

    assert result["fact_check_report"]["verdict"] == ""
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_verdict_prediction_preserves_existing_keys() -> None:
    llm = FakeLLM()
    agent = VerdictPredictionAgent(llm=llm)

    state: ArticleState = {
        **BASE_FC,
        "fact_check_report": {
            "claims": "test",
            "evidence": "test",
            "existing_key": "should_survive",
        },
    }
    result = await agent.run(state)

    assert result["fact_check_report"]["existing_key"] == "should_survive"
    assert "verdict" in result["fact_check_report"]


# =========== EvidenceRetrieval ===========


class FakeSearchProvider:
    def __init__(self):
        self.search_calls = []

    async def search(self, query: str, max_results: int = 5) -> list[str]:
        self.search_calls.append(query)
        return [f"Bukti untuk: {query}"]

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_evidence_retrieval_uses_queries() -> None:
    llm = FakeLLM()
    agent = EvidenceRetrievalAgent(llm=llm, search_provider=FakeSearchProvider())

    state: ArticleState = {**BASE_FC, "fact_check_report": {"queries": "inflasi Indonesia 2025"}}
    result = await agent.run(state)

    assert "evidence" in result["fact_check_report"]
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_evidence_retrieval_with_empty_queries() -> None:
    llm = FakeLLM()
    agent = EvidenceRetrievalAgent(llm=llm, search_provider=FakeSearchProvider())

    state: ArticleState = {**BASE_FC, "fact_check_report": {"queries": ""}}
    result = await agent.run(state)

    assert "evidence" in result["fact_check_report"]
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_evidence_retrieval_skips_blank_query_lines() -> None:
    llm = FakeLLM()
    agent = EvidenceRetrievalAgent(llm=llm, search_provider=FakeSearchProvider())

    state: ArticleState = {
        **BASE_FC,
        "fact_check_report": {"queries": "query1\n\n\nquery2\n  \nquery3"},
    }
    result = await agent.run(state)

    assert "evidence" in result["fact_check_report"]


@pytest.mark.asyncio
async def test_evidence_retrieval_preserves_existing_keys() -> None:
    llm = FakeLLM()
    agent = EvidenceRetrievalAgent(llm=llm, search_provider=FakeSearchProvider())

    state: ArticleState = {
        **BASE_FC,
        "fact_check_report": {"queries": "test query", "existing_key": "should_survive"},
    }
    result = await agent.run(state)

    assert result["fact_check_report"]["existing_key"] == "should_survive"
    assert "evidence" in result["fact_check_report"]


# =========== Chain integration ===========


@pytest.mark.asyncio
async def test_fact_check_chain_passes_data() -> None:
    llm = FakeLLM()
    ingestion = InputIngestionAgent(llm=llm)
    query_gen = QueryGenerationAgent(llm=llm)
    evidence_ret = EvidenceRetrievalAgent(llm=llm, search_provider=FakeSearchProvider())
    verdict = VerdictPredictionAgent(llm=llm)

    state: ArticleState = {**BASE_FC}
    state = await ingestion.run(state)
    assert "claims" in state["fact_check_report"]

    state = await query_gen.run(state)
    assert "queries" in state["fact_check_report"]

    state = await evidence_ret.run(state)
    assert "evidence" in state["fact_check_report"]

    state = await verdict.run(state)
    assert "verdict" in state["fact_check_report"]
