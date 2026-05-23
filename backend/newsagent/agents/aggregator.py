import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.cost.token_budget import with_budget
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class AggregatorAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    @with_budget(max_tokens=4000)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[Aggregator] mulai — article_id=%s", state["article_id"])

        try:
            article_source = state.get("edited_draft") or state["draft"]
            result = await self.llm.complete(
                system=self._system_prompt(),
                prompt=(
                    f"Artikel (edited):\n{article_source}\n\n"
                    f"Laporan Fact-Check:\n{state.get('fact_check_report', {})}\n\n"
                    "Lakukan debat 2 ronde dan berikan artikel final."
                ),
            )
            article = result
        except Exception as e:
            logger.error("[Aggregator] gagal: %s", e)
            article = state.get("edited_draft") or state["draft"]

        return {
            **state,
            "aggregated_article": article,
            "events": state["events"]
            + [make_event("Aggregator", "debate_and_consensus", f"artikel final ({len(article)} chars)")],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("aggregator.md")
