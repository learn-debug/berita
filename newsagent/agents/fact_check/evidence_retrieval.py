import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)


class EvidenceRetrievalAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm
        self.search = WebSearchTool()

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[EvidenceRetrieval] mulai — article_id=%s", state["article_id"])

        queries = state.get("fact_check_report", {}).get("queries", "")
        result = await self.llm.complete(
            system=self._system_prompt(),
            prompt=f"Cari bukti untuk query-query berikut:\n\n{queries}",
        )

        return {
            **state,
            "events": state["events"] + [make_event("EvidenceRetrieval", "retrieve_evidence", result[:200])],
        }

    def _system_prompt(self) -> str:
        return "Kumpulkan bukti dari sumber kredibel untuk setiap query. Prioritaskan sumber primer dan data resmi."
