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
        try:
            result = await self.llm.complete(
                system=self._system_prompt(),
                prompt=f"Buat query pencarian untuk memverifikasi klaim-klaim berikut:\n\n{claims}",
            )
            queries = result
        except Exception as e:
            logger.error("[QueryGeneration] gagal: %s", e)
            queries = ""

        fact_check = {**state.get("fact_check_report", {}), "queries": queries}

        return {
            **state,
            "fact_check_report": fact_check,
            "events": state["events"]
            + [make_event("QueryGeneration", "generate_queries", f"{len(queries)} chars")],
        }

    def _system_prompt(self) -> str:
        return "Buat query pencarian web yang tepat untuk memverifikasi setiap klaim. Fokus pada sumber kredibel."
