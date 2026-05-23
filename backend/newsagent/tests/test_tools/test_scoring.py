from newsagent.tools.scoring import compute_credibility, routing


class TestComputeCredibility:
    def test_perfect_score(self) -> None:
        assert compute_credibility(1.0, 1.0, 1.0, 1.0) == 1.0

    def test_zero_score(self) -> None:
        assert compute_credibility(0.0, 0.0, 0.0, 0.0) == 0.0

    def test_weighted_average(self) -> None:
        score = compute_credibility(1.0, 0.5, 0.5, 0.5)
        expected = round(0.40 * 1.0 + 0.25 * 0.5 + 0.20 * 0.5 + 0.15 * 0.5, 2)
        assert score == expected

    def test_clamps_negative(self) -> None:
        assert compute_credibility(-0.5, 0.0, 0.0, 0.0) == 0.0

    def test_clamps_above_one(self) -> None:
        assert compute_credibility(2.0, 2.0, 2.0, 2.0) == 1.0

    def test_partial_values(self) -> None:
        score = compute_credibility(fact_accuracy=0.8)
        expected = round(0.40 * 0.8, 2)
        assert score == expected

    def test_only_one_dimension(self) -> None:
        assert compute_credibility(narrative_consistency=1.0) == 0.25

    def test_all_defaults(self) -> None:
        assert compute_credibility() == 0.0


class TestRouting:
    def test_auto_publish(self) -> None:
        assert routing(0.75) == "auto-publish"
        assert routing(0.80) == "auto-publish"
        assert routing(1.0) == "auto-publish"

    def test_editor_review(self) -> None:
        assert routing(0.50) == "editor-review"
        assert routing(0.60) == "editor-review"
        assert routing(0.74) == "editor-review"

    def test_full_revision(self) -> None:
        assert routing(0.0) == "full-revision"
        assert routing(0.25) == "full-revision"
        assert routing(0.49) == "full-revision"

    def test_boundary_values(self) -> None:
        assert routing(0.75) == "auto-publish"
        assert routing(0.749999) == "editor-review"
        assert routing(0.50) == "editor-review"
        assert routing(0.499999) == "full-revision"

    def test_exact_auto_publish_threshold(self) -> None:
        assert routing(0.75) == "auto-publish"

    def test_exact_editor_review_threshold(self) -> None:
        assert routing(0.50) == "editor-review"

    def test_negative_score(self) -> None:
        assert routing(-0.1) == "full-revision"
