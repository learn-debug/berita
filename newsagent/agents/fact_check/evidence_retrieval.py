import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.tools.web_search import WebSearchTool
from newsagent.security.prompt_hardening import PromptHardener

logger = logging.getLogger(__name__)


class EvidenceRetrievalAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm
        self.search = WebSearchTool()

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[EvidenceRetrieval] mulai — article_id=%s", state["article_id"])

        queries = state.get("fact_check_report", {}).get("queries", "")
        try:
            results = []
            for q in queries.split("\n"):
                q = q.strip()
                if q:
                    page = await self.search.search(q)
                    if page:
                        results.append(page)
            evidence = "\n\n".join(results[:3]) if results else ""

            if not evidence:
                result = await self.llm.complete(
                    system=self._system_prompt(),
                    prompt=PromptHardener.wrap_user_input(f"Cari bukti untuk query-query berikut:\n\n{queries}"),
                )
                evidence = result
        except Exception as e:
            logger.error("[EvidenceRetrieval] gagal: %s", e)
            evidence = ""

        fact_check = {**state.get("fact_check_report", {}), "evidence": evidence}

        return {
            **state,
            "fact_check_report": fact_check,
            "events": state["events"]
            + [make_event("EvidenceRetrieval", "retrieve_evidence", f"{len(evidence)} chars")],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + (
            "Kumpulkan bukti dari sumber kredibel untuk setiap query. "
            "Prioritaskan sumber primer dan data resmi."
        )
