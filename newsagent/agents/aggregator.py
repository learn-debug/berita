import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener

logger = logging.getLogger(__name__)


class AggregatorAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[Aggregator] mulai — article_id=%s", state["article_id"])

        try:
            result = await self.llm.complete(
                system=self._system_prompt(),
                prompt=PromptHardener.wrap_user_input((
                    f"Artikel (edited):\n{state.get('edited_draft', state['draft'])}\n\n"
                    f"Laporan Fact-Check:\n{state.get('fact_check_report', {})}\n\n"
                    "Lakukan debat 2 ronde dan berikan artikel final."
                )),
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
        return PromptHardener.SYSTEM_GUARD + "\n\n" + (
            "Kamu adalah aggregator berita. Lakukan debat 2 ronde: "
            "Ronde 1: nilai artikel secara independen dari sudut pandang yang berbeda. "
            "Ronde 2: deteksi konflik dan capai konsensus. "
            "Kembalikan artikel final yang sudah disepakati."
        )
