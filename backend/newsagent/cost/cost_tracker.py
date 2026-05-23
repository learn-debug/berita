from datetime import datetime, timezone
from typing import Any

RATES: dict[str, float] = {
    "claude-sonnet-4-20250514": 3.0 / 1_000_000,
    "gpt-4o": 2.5 / 1_000_000,
}


class CostTracker:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def record(self, agent: str, model: str, input_tokens: int, output_tokens: int) -> None:
        rate = RATES.get(model, 1.0 / 1_000_000)
        cost = (input_tokens + output_tokens) * rate
        self._entries.append(
            {
                "agent": agent,
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost": round(cost, 6),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def total_cost(self) -> float:
        return round(sum(e["cost"] for e in self._entries), 6)

    def summary(self) -> dict[str, Any]:
        return {
            "total_cost": self.total_cost(),
            "total_requests": len(self._entries),
            "entries": self._entries,
        }
