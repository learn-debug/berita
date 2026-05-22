import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry

logger = logging.getLogger(__name__)


class QueryGenerationAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[QueryGeneration] mulai — article_id=%s", state["article_id"])

        claims = state.get("fact_check_report", {}).get("claims", "")
        result = await self.llm.complete(
            system=self._system_prompt(),
            prompt=f"Buat query pencarian untuk memverifikasi klaim-klaim berikut:\n\n{claims}",
        )

        return {
            **state,
            "events": state["events"] + [make_event("QueryGeneration", "generate_queries", result[:200])],
        }

    def _system_prompt(self) -> str:
        return "Buat query pencarian web yang tepat untuk memverifikasi setiap klaim. Fokus pada sumber kredibel."
