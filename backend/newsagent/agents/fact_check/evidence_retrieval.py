import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.tools.search_factory import search_provider_factory
from newsagent.tools.search_provider import SearchProvider
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class EvidenceRetrievalAgent:
    def __init__(self, llm: BaseLLMAdapter, search_provider: SearchProvider | None = None):
        self.llm = llm
        self.search = search_provider or search_provider_factory()

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[EvidenceRetrieval] mulai — article_id=%s", state["article_id"])

        queries = state.get("fact_check_report", {}).get("queries", "")
        try:
            results = []
            for q in queries.split("\n"):
                q = q.strip()
                if q:
                    pages = await self.search.search(q)
                    results.extend(pages)
            evidence = "\n\n---\n\n".join(results[:3]) if results else ""

            if not evidence:
                prompt = PromptHardener.wrap_user_input(f"Cari bukti untuk query-query berikut:\n\n{queries}")
                result = await self.llm.complete(
                    system=self._system_prompt(),
                    prompt=prompt,
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
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("fact_check/evidence_retrieval.md")
