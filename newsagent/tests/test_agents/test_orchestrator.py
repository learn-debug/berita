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
