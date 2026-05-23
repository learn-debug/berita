from newsagent.cost.cost_tracker import CostTracker


class TestCostTracker:
    def test_record_adds_entry(self) -> None:
        ct = CostTracker()
        ct.record("orchestrator", "claude-sonnet-4-20250514", 1000, 500)
        assert ct.total_cost() > 0.0
        assert ct.summary()["total_requests"] == 1

    def test_total_cost_multiple_entries(self) -> None:
        ct = CostTracker()
        ct.record("agent1", "claude-sonnet-4-20250514", 1000, 500)
        ct.record("agent2", "gpt-4o", 2000, 1000)
        assert ct.summary()["total_requests"] == 2
        assert ct.total_cost() > 0.0

    def test_total_cost_empty(self) -> None:
        ct = CostTracker()
        assert ct.total_cost() == 0.0
        assert ct.summary()["total_requests"] == 0

    def test_summary_structure(self) -> None:
        ct = CostTracker()
        ct.record("test", "claude-sonnet-4-20250514", 100, 50)
        summary = ct.summary()
        assert "total_cost" in summary
        assert "total_requests" in summary
        assert "entries" in summary
        assert len(summary["entries"]) == 1
        assert "timestamp" in summary["entries"][0]

    def test_unknown_model_uses_default_rate(self) -> None:
        ct = CostTracker()
        ct.record("test", "unknown-model", 1000, 500)
        assert ct.total_cost() > 0.0
        assert ct.total_cost() == round(1500 * 1.0 / 1_000_000, 6)

    def test_negative_tokens(self) -> None:
        ct = CostTracker()
        ct.record("test", "claude-sonnet-4-20250514", -100, -50)
        cost = ct.total_cost()
        assert cost <= 0.0
