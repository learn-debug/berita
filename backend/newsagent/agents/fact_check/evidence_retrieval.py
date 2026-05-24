import asyncio
import logging
from typing import cast

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState, FactCheckReport
from newsagent.cost.token_budget import with_budget
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.tools.search_factory import search_provider_factory
from newsagent.tools.search_provider import SearchProvider
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

TEXT_OUTPUT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {"output": {"type": "string"}},
    "required": ["output"],
}


class EvidenceRetrievalAgent:
    def __init__(self, llm: BaseLLMAdapter, search_provider: SearchProvider | None = None):
        self.llm = llm
        self.search = search_provider or search_provider_factory()

    @with_retry(max_attempts=3)
    @with_budget(max_tokens=1024)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[EvidenceRetrieval] mulai — article_id=%s", state["article_id"])

        queries = state.get("fact_check_report", {}).get("queries", "")
        try:
            query_list = [q.strip() for q in queries.split("\n") if q.strip()]

            if query_list:
                tasks = [self.search.search(q) for q in query_list]
                results_nested = await asyncio.gather(*tasks, return_exceptions=True)
                results: list[str] = []
                for pages in results_nested:
                    if isinstance(pages, Exception):
                        logger.warning("[EvidenceRetrieval] search gagal: %s", pages)
                        continue
                    for p in pages:
                        if len(p) > 2000:
                            p = p[:2000] + "\n...[truncated]"
                        results.append(p)
                evidence = "\n\n---\n\n".join(results[:15]) if results else ""
            else:
                evidence = ""

            if not evidence:
                prompt = PromptHardener.wrap_user_input(f"Cari bukti untuk query-query berikut:\n\n{queries}")
                result = await self.llm.complete_structured(
                    system=self._system_prompt(),
                    prompt=prompt,
                    schema=TEXT_OUTPUT_SCHEMA,
                )
                evidence = result.get("output", "") if isinstance(result, dict) else ""
        except Exception as e:
            logger.error("[EvidenceRetrieval] gagal: %s", e)
            evidence = ""

        fact_check = cast(FactCheckReport, {**state.get("fact_check_report", {}), "evidence": evidence})

        return {
            **state,
            "fact_check_report": fact_check,
            "events": state["events"]
            + [make_event("EvidenceRetrieval", "retrieve_evidence", f"{len(evidence)} chars")],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("fact_check/evidence_retrieval.md")

    async def close(self) -> None:
        await self.search.close()
