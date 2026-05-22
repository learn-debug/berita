from newsagent.tools.scoring import compute_credibility, routing


def test_compute_credibility_perfect() -> None:
    score = compute_credibility(1.0, 1.0, 1.0, 1.0)
    assert score == 1.0


def test_compute_credibility_zero() -> None:
    score = compute_credibility(0.0, 0.0, 0.0, 0.0)
    assert score == 0.0


def test_routing_auto_publish() -> None:
    assert routing(0.80) == "auto-publish"


def test_routing_editor_review() -> None:
    assert routing(0.60) == "editor-review"


def test_routing_full_revision() -> None:
    assert routing(0.30) == "full-revision"
