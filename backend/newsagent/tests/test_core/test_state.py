from newsagent.core.state import ArticleState, ArticleStatus, transition_allowed


def _make_state(overrides: dict | None = None) -> ArticleState:
    base: ArticleState = {
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
        "revision_count": 0,
        "events": [],
    }
    if overrides:
        base.update(overrides)
    return base


def test_article_state_defaults() -> None:
    state = _make_state()
    assert state["article_id"] == ""
    assert state["status"] == "idle"
    assert state["events"] == []


def test_article_state_immutable_pattern() -> None:
    state = _make_state({"article_id": "abc", "raw_input": "test", "status": "processing"})
    new_state: ArticleState = {
        **state,
        "draft": "draft content",
        "events": [
            {
                "agent": "test",
                "action": "run",
                "detail": None,
                "timestamp": "2024-01-01T00:00:00",
                "metadata": {},
            }
        ],
    }
    assert state["draft"] == ""
    assert new_state["draft"] == "draft content"
    assert len(new_state["events"]) == 1
    assert len(state["events"]) == 0


def test_transition_allowed_processing_to_review() -> None:
    assert transition_allowed(ArticleStatus.PROCESSING, ArticleStatus.REVIEW)


def test_transition_allowed_processing_to_revision() -> None:
    assert transition_allowed(ArticleStatus.PROCESSING, ArticleStatus.REVISION)


def test_transition_allowed_processing_to_published() -> None:
    assert transition_allowed(ArticleStatus.PROCESSING, ArticleStatus.PUBLISHED)


def test_transition_allowed_processing_to_failed() -> None:
    assert transition_allowed(ArticleStatus.PROCESSING, ArticleStatus.FAILED)


def test_transition_allowed_review_to_approved() -> None:
    assert transition_allowed(ArticleStatus.REVIEW, ArticleStatus.APPROVED)


def test_transition_allowed_review_to_rejected() -> None:
    assert transition_allowed(ArticleStatus.REVIEW, ArticleStatus.REJECTED)


def test_transition_allowed_review_to_processing_retry() -> None:
    assert transition_allowed(ArticleStatus.REVIEW, ArticleStatus.PROCESSING)


def test_transition_allowed_revision_to_processing() -> None:
    assert transition_allowed(ArticleStatus.REVISION, ArticleStatus.PROCESSING)


def test_transition_allowed_approved_to_published() -> None:
    assert transition_allowed(ArticleStatus.APPROVED, ArticleStatus.PUBLISHED)


def test_transition_allowed_failed_to_processing_retry() -> None:
    assert transition_allowed(ArticleStatus.FAILED, ArticleStatus.PROCESSING)


def test_transition_disallowed_published_to_processing() -> None:
    assert not transition_allowed(ArticleStatus.PUBLISHED, ArticleStatus.PROCESSING)


def test_transition_disallowed_rejected_to_approved() -> None:
    assert not transition_allowed(ArticleStatus.REJECTED, ArticleStatus.APPROVED)


def test_transition_disallowed_pending_to_published() -> None:
    assert not transition_allowed(ArticleStatus.PENDING, ArticleStatus.PUBLISHED)


def test_transition_allowed_with_string_values() -> None:
    assert transition_allowed("processing", "review")
    assert not transition_allowed("published", "processing")


def test_transition_allows_unknown_status() -> None:
    assert transition_allowed("idle", "processing")
