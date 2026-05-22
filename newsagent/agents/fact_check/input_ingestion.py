import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry

logger = logging.getLogger(__name__)


class InputIngestionAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[InputIngestion] mulai — article_id=%s", state["article_id"])

        source = state.get("edited_draft") or state["draft"]
        result = await self.llm.complete(
            system=self._system_prompt(),
            prompt=f"Ekstrak klaim-klaim faktual dari artikel berikut:\n\n{source}",
        )

        return {
            **state,
            "events": state["events"] + [make_event("InputIngestion", "extract_claims", result[:200])],
        }

    def _system_prompt(self) -> str:
        return "Ekstrak semua klaim faktual yang dapat diverifikasi dari artikel di bawah ini. Kembalikan sebagai daftar terpisah."
