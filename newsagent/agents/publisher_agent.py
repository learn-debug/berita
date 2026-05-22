import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry

logger = logging.getLogger(__name__)


class PublisherAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[PublisherAgent] mulai — article_id=%s", state["article_id"])

        content = state.get("aggregated_article") or state.get("edited_draft") or state["draft"]

        try:
            result = await self.llm.complete(
                system=self._system_prompt(),
                prompt=f"Buat judul dan siapkan artikel berikut untuk publikasi:\n\n{content}",
            )
            logger.info("[PublisherAgent] selesai — %d karakter", len(result))
        except Exception as e:
            logger.error("[PublisherAgent] gagal: %s", e)

        return {
            **state,
            "status": "published",
            "events": state["events"]
            + [make_event("PublisherAgent", "publish_article", "artikel dipublikasikan")],
        }
