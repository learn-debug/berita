import logging
from typing import cast

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState, FactCheckReport
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

TEXT_OUTPUT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {"output": {"type": "string"}},
    "required": ["output"],
}


class QueryGenerationAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[QueryGeneration] mulai — article_id=%s", state["article_id"])

        claims = state.get("fact_check_report", {}).get("claims", "")
        try:
            prompt = PromptHardener.wrap_user_input(
                f"Buat query pencarian untuk memverifikasi klaim-klaim berikut:\n\n{claims}"
            )
            result = await self.llm.complete_structured(
                system=self._system_prompt(),
                prompt=prompt,
                schema=TEXT_OUTPUT_SCHEMA,
                max_tokens=1024,
            )
            queries = result.get("output", "") if isinstance(result, dict) else ""
        except Exception as e:
            logger.error("[QueryGeneration] gagal: %s", e)
            queries = ""

        fact_check = cast(FactCheckReport, {**state.get("fact_check_report", {}), "queries": queries})

        return {
            **state,
            "fact_check_report": fact_check,
            "events": state["events"]
            + [make_event("QueryGeneration", "generate_queries", f"{len(queries)} chars")],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("fact_check/query_generation.md")
