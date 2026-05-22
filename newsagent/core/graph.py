from typing import Any

from langgraph.graph import END, StateGraph

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
from newsagent.core.config import settings
from newsagent.core.state import ArticleState
from newsagent.llm.adapter_factory import adapter_factory
from newsagent.rag.pipeline import RAGPipeline
from newsagent.tools.cms_client import CMSClient


def route_after_quality(state: ArticleState) -> str:
    score = state.get("credibility_score", 0.0)
    if score >= 0.75:
        return "publisher"
    if score >= 0.50:
        return "editor_agent"
    return "orchestrator"
    return "orchestrator"


def route_after_draft(state: ArticleState) -> str:
    status = state.get("status", "")
    if status == "revision":
        return "orchestrator"
    return "editor_agent"


def build_graph() -> Any:
    orchestrator = OrchestratorAgent()
    rag_pipeline = RAGPipeline(llm=adapter_factory("rag"))
    draft = DraftAgent(llm=adapter_factory("draft_agent"))
    editor = EditorAgent(llm=adapter_factory("editor_agent"))
    input_ingestion = InputIngestionAgent(llm=adapter_factory("fact_check"))
    query_gen = QueryGenerationAgent(llm=adapter_factory("fact_check"))
    evidence_ret = EvidenceRetrievalAgent(llm=adapter_factory("fact_check"))
    verdict = VerdictPredictionAgent(llm=adapter_factory("fact_check"))
    aggregator = AggregatorAgent(llm=adapter_factory("orchestrator"))
    quality = QualityGateAgent(llm=adapter_factory("orchestrator"))
    cms = (
        CMSClient(base_url=settings.cms_base_url, api_key=settings.cms_api_key)
        if settings.cms_base_url and settings.cms_api_key
        else None
    )
    publisher = PublisherAgent(llm=adapter_factory("publisher_agent"), cms=cms)

    workflow = StateGraph(ArticleState)

    workflow.add_node("orchestrator", orchestrator.run)
    workflow.add_node("rag_pipeline", rag_pipeline.run)
    workflow.add_node("draft_agent", draft.run)
    workflow.add_node("editor_agent", editor.run)
    workflow.add_node("input_ingestion", input_ingestion.run)
    workflow.add_node("query_generation", query_gen.run)
    workflow.add_node("evidence_retrieval", evidence_ret.run)
    workflow.add_node("verdict_prediction", verdict.run)
    workflow.add_node("aggregator", aggregator.run)
    workflow.add_node("quality_gate", quality.run)
    workflow.add_node("publisher", publisher.run)

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
    workflow.add_edge("publisher", END)

    return workflow.compile()
