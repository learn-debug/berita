import pytest

from newsagent.agents.aggregator import AggregatorAgent
from newsagent.agents.draft_agent import DraftAgent
from newsagent.agents.editor_agent import EditorAgent
from newsagent.agents.fact_check.evidence_retrieval import EvidenceRetrievalAgent
from newsagent.agents.fact_check.input_ingestion import InputIngestionAgent
from newsagent.agents.fact_check.query_generation import QueryGenerationAgent
from newsagent.agents.fact_check.verdict_prediction import VerdictPredictionAgent
from newsagent.agents.orchestrator import OrchestratorAgent
from newsagent.agents.publisher_agent import PublisherAgent
from newsagent.agents.quality_gate import QualityGateAgent
from newsagent.core.state import ArticleState


class FakeLLMDraft:
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return "Ini adalah draft artikel yang dihasilkan."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


class FakeLLMEditor:
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return "Ini adalah artikel yang sudah diedit dengan baik."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


class FakeLLMGeneric:
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return "Respon dari LLM."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
        required = schema.get("required", [])
        if "judul" in required:
            return {"judul": "Judul Artikel", "konten": "Respon dari LLM."}
        if "claims" in required:
            return {
                "claims": [
                    {
                        "claim": "Test claim",
                        "premis_fakta": "Test premis fakta",
                        "premis_bukti": "Test premis bukti",
                        "premis_sumber": "Test sumber — TINGGI",
                        "analisis": "Test analisis",
                        "putusan": "SUPPORTED",
                        "alasan": "Test alasan",
                        "keyakinan": "TINGGI",
                    }
                ]
            }
        return {}

    def model_name(self) -> str:
        return "fake"


class FakeLLMQuality:
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return ""

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
        return {
            "fact_accuracy": 0.80,
            "narrative_consistency": 0.75,
            "conflict_resolution": 0.70,
            "source_quality": 0.65,
        }

    def model_name(self) -> str:
        return "fake"


class HighScoreLLM:
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return ""

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
        return {
            "fact_accuracy": 0.90,
            "narrative_consistency": 0.85,
            "conflict_resolution": 0.80,
            "source_quality": 0.95,
        }

    def model_name(self) -> str:
        return "fake"


@pytest.mark.asyncio
async def test_pipeline_orchestrator_to_draft() -> None:
    orchestrator = OrchestratorAgent()
    draft = DraftAgent(llm=FakeLLMDraft())

    state: ArticleState = {
        "article_id": "",
        "input_type": "topic",
        "raw_input": "Dampak AI di Indonesia",
        "rag_context": "Konteks tentang AI.",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "idle",
        "events": [],
    }

    state = await orchestrator.run(state)
    assert state["article_id"] != ""
    assert state["status"] == "processing"

    state = await draft.run(state)
    assert state["draft"] != ""
    assert len(state["events"]) == 2


@pytest.mark.asyncio
async def test_pipeline_draft_to_editor() -> None:
    draft = DraftAgent(llm=FakeLLMDraft())
    editor = EditorAgent(llm=FakeLLMEditor())

    state: ArticleState = {
        "article_id": "test-pipe",
        "input_type": "topic",
        "raw_input": "Topik test",
        "rag_context": "Konteks",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }

    state = await draft.run(state)
    assert state["draft"] != ""

    state = await editor.run(state)
    assert state["edited_draft"] != ""
    assert len(state["events"]) == 2


@pytest.mark.asyncio
async def test_pipeline_fact_check_chain() -> None:
    llm = FakeLLMGeneric()
    ingestion = InputIngestionAgent(llm=llm)
    query_gen = QueryGenerationAgent(llm=llm)
    evidence_ret = EvidenceRetrievalAgent(llm=llm)
    verdict = VerdictPredictionAgent(llm=llm)

    state: ArticleState = {
        "article_id": "fc-pipe",
        "input_type": "draft",
        "raw_input": "Test",
        "rag_context": "",
        "draft": "Presiden mengatakan inflasi turun 5%.",
        "fact_check_report": {},
        "edited_draft": "Presiden mengatakan inflasi turun 5%.",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }

    state = await ingestion.run(state)
    assert "claims" in state["fact_check_report"]

    state = await query_gen.run(state)
    assert "queries" in state["fact_check_report"]

    state = await evidence_ret.run(state)
    assert "evidence" in state["fact_check_report"]

    state = await verdict.run(state)
    assert "verdict" in state["fact_check_report"]


@pytest.mark.asyncio
async def test_pipeline_aggregator_to_quality_gate() -> None:
    aggregator = AggregatorAgent(llm=FakeLLMGeneric())
    quality = QualityGateAgent(llm=FakeLLMQuality())

    state: ArticleState = {
        "article_id": "aq-pipe",
        "input_type": "topic",
        "raw_input": "Test",
        "rag_context": "",
        "draft": "Draft artikel untuk diagregasi.",
        "fact_check_report": {"claims": "test", "verdict": "SUPPORTED"},
        "edited_draft": "Draft yang sudah diedit.",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }

    state = await aggregator.run(state)
    assert state["aggregated_article"] != ""

    state = await quality.run(state)
    assert state["credibility_score"] > 0.0


@pytest.mark.asyncio
async def test_pipeline_quality_gate_to_publisher() -> None:
    quality = QualityGateAgent(llm=HighScoreLLM())
    publisher = PublisherAgent(llm=FakeLLMGeneric())

    state: ArticleState = {
        "article_id": "qp-pipe",
        "input_type": "topic",
        "raw_input": "Test",
        "rag_context": "",
        "draft": "Draft artikel.",
        "fact_check_report": {},
        "edited_draft": "Draf diedit.",
        "aggregated_article": "Artikel final.",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }

    state = await quality.run(state)
    assert state["credibility_score"] >= 0.80
    assert state["status"] == "processing"

    state = await publisher.run(state)
    assert state["status"] == "published"
    assert len(state["events"]) == 2
