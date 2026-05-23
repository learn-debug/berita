from unittest.mock import patch

import pytest

from newsagent.agents.orchestrator import OrchestratorAgent
from newsagent.core.state import ArticleState


@pytest.mark.asyncio
async def test_orchestrator_sets_article_id() -> None:
    agent = OrchestratorAgent()

    state: ArticleState = {
        "article_id": "",
        "input_type": "topic",
        "raw_input": "Test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "idle",
        "events": [],
    }

    result = await agent.run(state)

    assert result["article_id"] != ""
    assert result["status"] == "processing"


@pytest.mark.asyncio
async def test_orchestrator_preserves_existing_article_id() -> None:
    agent = OrchestratorAgent()

    state: ArticleState = {
        "article_id": "existing-id",
        "input_type": "topic",
        "raw_input": "Test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "idle",
        "events": [],
    }

    result = await agent.run(state)

    assert result["article_id"] == "existing-id"
    assert result["status"] == "processing"


@pytest.mark.asyncio
async def test_orchestrator_appends_events() -> None:
    agent = OrchestratorAgent()

    state: ArticleState = {
        "article_id": "",
        "input_type": "topic",
        "raw_input": "Test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "idle",
        "events": [{"agent": "previous", "action": "done"}],
    }

    result = await agent.run(state)

    assert len(result["events"]) == 2
    assert result["events"][0]["agent"] == "previous"


@pytest.mark.asyncio
async def test_orchestrator_handles_exception() -> None:
    agent = OrchestratorAgent()

    state: ArticleState = {
        "article_id": "",
        "input_type": "topic",
        "raw_input": "Test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "idle",
        "events": [],
    }

    call_count = 0

    def _mock_make_event(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("error")
        return {"agent": "orchestrator", "action": "failed", "detail": str(args)}

    with patch("newsagent.agents.orchestrator.make_event", side_effect=_mock_make_event):
        result = await agent.run(state)

    assert result["status"] == "failed"
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_orchestrator_with_draft_input_type() -> None:
    agent = OrchestratorAgent()

    state: ArticleState = {
        "article_id": "",
        "input_type": "draft",
        "raw_input": "Ini adalah draf mentah.",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "idle",
        "events": [],
    }

    result = await agent.run(state)

    assert result["article_id"] != ""
    assert result["status"] == "processing"
