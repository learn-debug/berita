import time
from collections.abc import Callable
from typing import Any

from langgraph.graph import END, StateGraph

from newsagent.agents.aggregator import AggregatorAgent
from newsagent.agents.draft_agent import DraftAgent
from newsagent.agents.editor_agent import EditorAgent
from newsagent.agents.fact_check.evidence_retrieval import EvidenceRetrievalAgent
from newsagent.agents.fact_check.input_ingestion import InputIngestionAgent
from newsagent.agents.fact_check.query_generation import QueryGenerationAgent
from newsagent.agents.fact_check.verdict_prediction import VerdictPredictionAgent
from newsagent.agents.memory_agent import MemoryAgent
from newsagent.agents.orchestrator import OrchestratorAgent
from newsagent.agents.publisher_agent import PublisherAgent
from newsagent.agents.quality_gate import QualityGateAgent
from newsagent.core.config import settings
from newsagent.core.state import ArticleState, ArticleStatus
from newsagent.database.kg_repository import KnowledgeGraphRepository
from newsagent.llm.adapter_factory import adapter_factory
from newsagent.memory.draft_memory import DraftMemory
from newsagent.memory.verdict_cache import VerdictCache
from newsagent.rag.pipeline import RAGPipeline
from newsagent.tools.cms_client import CMSClient

MAX_REVISIONS = 2


def route_after_quality(state: ArticleState) -> str:
    score = state.get("credibility_score", 0.0)
    revisions = state.get("revision_count", 0)
    if score >= 0.75:
        return "memory_agent"
    if score >= 0.50:
        if revisions < MAX_REVISIONS:
            return "editor_agent"
        return "memory_agent"
    if revisions < MAX_REVISIONS:
        return "orchestrator"
    return "memory_agent"


def route_after_draft(state: ArticleState) -> str:
    status = state.get("status", "")
    if status == ArticleStatus.REVISION.value:
        return "orchestrator"
    return "editor_agent"


def _wrap_node(
    name: str,
    fn: Callable[[ArticleState], Any],
    event_bus: Any | None,
) -> Callable[[ArticleState], Any]:
    if event_bus is None:
        return fn

    async def wrapped(state: ArticleState) -> Any:
        article_id = state.get("article_id", "")
        await event_bus.publish(
            article_id,
            {
                "type": "agent_start",
                "agent": name,
                "timestamp": time.time(),
            },
        )
        try:
            result = await fn(state)
            await event_bus.publish(
                article_id,
                {
                    "type": "agent_complete",
                    "agent": name,
                    "timestamp": time.time(),
                },
            )
            return result
        except Exception as e:
            await event_bus.publish(
                article_id,
                {
                    "type": "agent_error",
                    "agent": name,
                    "error": str(e),
                    "timestamp": time.time(),
                },
            )
            raise

    return wrapped


def build_graph(cleanup_handlers: list | None = None, event_bus: Any | None = None) -> Any:
    draft_memory = DraftMemory()
    verdict_cache = VerdictCache()
    kg_repo = KnowledgeGraphRepository()

    orchestrator = OrchestratorAgent()
    rag_pipeline = RAGPipeline(llm=adapter_factory("rag"))
    draft = DraftAgent(llm=adapter_factory("draft_agent"), draft_memory=draft_memory)
    editor = EditorAgent(llm=adapter_factory("editor_agent"))
    input_ingestion = InputIngestionAgent(llm=adapter_factory("fact_check"))
    query_gen = QueryGenerationAgent(llm=adapter_factory("fact_check"))
    evidence_ret = EvidenceRetrievalAgent(llm=adapter_factory("fact_check"))
    verdict = VerdictPredictionAgent(llm=adapter_factory("fact_check"), cache=verdict_cache)
    aggregator = AggregatorAgent(llm=adapter_factory("orchestrator"))
    quality = QualityGateAgent(llm=adapter_factory("orchestrator"), draft_memory=draft_memory)
    memory = MemoryAgent(draft_memory=draft_memory, verdict_cache=verdict_cache, kg_repo=kg_repo)
    cms = (
        CMSClient(base_url=settings.cms_base_url, api_key=settings.cms_api_key)
        if settings.cms_base_url and settings.cms_api_key
        else None
    )
    publisher = PublisherAgent(llm=adapter_factory("publisher_agent"), cms=cms)

    if cms and cleanup_handlers is not None:
        cleanup_handlers.append(cms.close)

    if cleanup_handlers is not None:
        cleanup_handlers.append(evidence_ret.close)
        cleanup_handlers.append(rag_pipeline.close)

    workflow = StateGraph(ArticleState)

    workflow.add_node("orchestrator", _wrap_node("orchestrator", orchestrator.run, event_bus))
    workflow.add_node("rag_pipeline", _wrap_node("rag_pipeline", rag_pipeline.run, event_bus))
    workflow.add_node("draft_agent", _wrap_node("draft_agent", draft.run, event_bus))
    workflow.add_node("editor_agent", _wrap_node("editor_agent", editor.run, event_bus))
    workflow.add_node("input_ingestion", _wrap_node("input_ingestion", input_ingestion.run, event_bus))
    workflow.add_node("query_generation", _wrap_node("query_generation", query_gen.run, event_bus))
    workflow.add_node("evidence_retrieval", _wrap_node("evidence_retrieval", evidence_ret.run, event_bus))
    workflow.add_node("verdict_prediction", _wrap_node("verdict_prediction", verdict.run, event_bus))
    workflow.add_node("aggregator", _wrap_node("aggregator", aggregator.run, event_bus))
    workflow.add_node("quality_gate", _wrap_node("quality_gate", quality.run, event_bus))
    workflow.add_node("memory_agent", _wrap_node("memory_agent", memory.run, event_bus))
    workflow.add_node("publisher", _wrap_node("publisher", publisher.run, event_bus))

    workflow.set_entry_point("orchestrator")

    workflow.add_edge("orchestrator", "rag_pipeline")
    workflow.add_edge("rag_pipeline", "draft_agent")
    workflow.add_conditional_edges("draft_agent", route_after_draft)
    workflow.add_edge("editor_agent", "input_ingestion")
    workflow.add_edge("input_ingestion", "query_generation")
    workflow.add_edge("query_generation", "evidence_retrieval")
    workflow.add_edge("evidence_retrieval", "verdict_prediction")
    workflow.add_edge("verdict_prediction", "aggregator")
    workflow.add_edge("aggregator", "quality_gate")
    workflow.add_conditional_edges("quality_gate", route_after_quality)
    workflow.add_edge("memory_agent", "publisher")
    workflow.add_edge("publisher", END)

    return workflow.compile()
