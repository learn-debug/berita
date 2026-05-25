import pytest

from newsagent.core.graph import build_graph, route_after_draft, route_after_quality
from newsagent.core.state import ArticleState


def _make_state(overrides: dict | None = None) -> ArticleState:
    base: ArticleState = {
        "article_id": "graph-test",
        "input_type": "topic",
        "raw_input": "Test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }
    if overrides:
        base.update(overrides)
    return base


class TestRouteAfterQuality:
    def test_high_score_goes_to_memory_agent(self) -> None:
        state = _make_state({"credibility_score": 0.85})
        assert route_after_quality(state) == "memory_agent"

    def test_score_at_auto_publish_boundary(self) -> None:
        state = _make_state({"credibility_score": 0.75})
        assert route_after_quality(state) == "memory_agent"

    def test_score_at_review_boundary(self) -> None:
        state = _make_state({"credibility_score": 0.50})
        assert route_after_quality(state) == "editor_agent"

    def test_editor_review_upper_boundary(self) -> None:
        state = _make_state({"credibility_score": 0.74})
        assert route_after_quality(state) == "editor_agent"

    def test_low_score_goes_to_orchestrator(self) -> None:
        state = _make_state({"credibility_score": 0.30})
        assert route_after_quality(state) == "orchestrator"

    def test_zero_score_goes_to_orchestrator(self) -> None:
        state = _make_state({"credibility_score": 0.0})
        assert route_after_quality(state) == "orchestrator"

    def test_missing_score_goes_to_orchestrator(self) -> None:
        state = _make_state({})
        del state["credibility_score"]
        assert route_after_quality(state) == "orchestrator"

    def test_score_just_below_boundary(self) -> None:
        state = _make_state({"credibility_score": 0.4999})
        assert route_after_quality(state) == "orchestrator"


class TestRouteAfterDraft:
    def test_normal_status_goes_to_editor(self) -> None:
        state = _make_state({"status": "processing"})
        assert route_after_draft(state) == "editor_agent"

    def test_revision_status_goes_to_orchestrator(self) -> None:
        state = _make_state({"status": "revision"})
        assert route_after_draft(state) == "orchestrator"

    def test_empty_status_goes_to_editor(self) -> None:
        state = _make_state({"status": ""})
        assert route_after_draft(state) == "editor_agent"

    def test_missing_status_goes_to_editor(self) -> None:
        state = _make_state({})
        del state["status"]
        assert route_after_draft(state) == "editor_agent"


class TestBuildGraph:
    def test_build_graph_returns_compiled_graph(self) -> None:
        graph = build_graph()
        assert graph is not None

    @pytest.mark.asyncio
    async def test_graph_has_correct_nodes(self) -> None:
        graph = build_graph()
        nodes = list(graph.nodes.keys())
        expected = [
            "orchestrator",
            "rag_pipeline",
            "draft_agent",
            "editor_agent",
            "input_ingestion",
            "query_generation",
            "evidence_retrieval",
            "verdict_prediction",
            "aggregator",
            "quality_gate",
            "memory_agent",
            "publisher",
        ]
        for node in expected:
            assert node in nodes, f"Node '{node}' missing from graph"

    def test_graph_entry_point(self) -> None:
        graph = build_graph()
        node_names = list(graph.nodes.keys())
        assert node_names[1] == "orchestrator"
