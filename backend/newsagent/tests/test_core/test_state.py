from newsagent.core.state import ArticleState


def test_article_state_defaults() -> None:
    state: ArticleState = {
        "article_id": "",
        "input_type": "topic",
        "raw_input": "",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "idle",
        "events": [],
    }
    assert state["article_id"] == ""
    assert state["status"] == "idle"
    assert state["events"] == []


def test_article_state_immutable_pattern() -> None:
    state: ArticleState = {
        "article_id": "abc",
        "input_type": "topic",
        "raw_input": "test",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }
    new_state: ArticleState = {
        **state,
        "draft": "draft content",
        "events": [{"agent": "test", "action": "run"}],
    }
    assert state["draft"] == ""
    assert new_state["draft"] == "draft content"
    assert len(new_state["events"]) == 1
    assert len(state["events"]) == 0
