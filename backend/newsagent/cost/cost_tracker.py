import asyncio
import logging
import os
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

RATES: dict[str, float] = {
    "claude-sonnet-4-20250514": 3.0 / 1_000_000,
    "gpt-4o": 2.5 / 1_000_000,
    "mistral": 1.0 / 1_000_000,
}


def get_max_monthly_budget() -> float:
    # Default to 50.0 USD monthly budget, configurable via environment variables
    try:
        return float(os.getenv("MAX_MONTHLY_BUDGET", "50.0"))
    except ValueError:
        return 50.0


async def get_monthly_cost() -> float:
    try:
        from newsagent.memory.engine import get_engine

        engine = await get_engine()
        # Query total cost for current month in UTC
        total = await engine.fetchval(
            """
            SELECT SUM(cost) FROM agent_costs
            WHERE timestamp >= DATE_TRUNC('month', NOW() AT TIME ZONE 'UTC')
            """
        )
        return float(total or 0.0)
    except Exception as e:
        logger.warning("[CostTracker] failed to fetch monthly cost: %s", e)
        return 0.0


class CostTracker:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._db_task: asyncio.Task | None = None

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
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        self._schedule_db_write(agent, model, input_tokens, output_tokens, cost)

    def _schedule_db_write(
        self, agent: str, model: str, input_tokens: int, output_tokens: int, cost: float
    ) -> None:
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                task = loop.create_task(self._save_db(agent, model, input_tokens, output_tokens, cost))
                self._db_task = task
        except RuntimeError:
            pass

    async def _save_db(
        self, agent: str, model: str, input_tokens: int, output_tokens: int, cost: float
    ) -> None:
        try:
            from newsagent.memory.engine import get_engine

            engine = await get_engine()
            await engine.execute(
                """
                INSERT INTO agent_costs (agent, model, input_tokens, output_tokens, cost)
                VALUES ($1, $2, $3, $4, $5)
                """,
                agent,
                model,
                input_tokens,
                output_tokens,
                cost,
            )
        except Exception as e:
            logger.warning("[CostTracker] failed to write cost to DB: %s", e)

    def total_cost(self) -> float:
        return round(sum(e["cost"] for e in self._entries), 6)

    def summary(self) -> dict[str, Any]:
        return {
            "total_cost": self.total_cost(),
            "total_requests": len(self._entries),
            "entries": self._entries,
        }
