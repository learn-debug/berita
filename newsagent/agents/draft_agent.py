import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry

logger = logging.getLogger(__name__)


class DraftAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[DraftAgent] mulai — article_id=%s", state["article_id"])

        result = await self.llm.complete(
            system=self._system_prompt(),
            prompt=f"Topik: {state['raw_input']}\n\nKonteks RAG:\n{state['rag_context']}",
        )

        logger.info("[DraftAgent] selesai — %d karakter", len(result))

        return {
            **state,
            "draft": result,
            "events": state["events"]
            + [make_event("DraftAgent", "generate_draft", f"draft selesai ({len(result)} chars)")],
        }

    def _system_prompt(self) -> str:
        return (
            "Kamu adalah jurnalis senior. Buat artikel berita yang informatif dan terstruktur "
            "berdasarkan topik dan konteks RAG yang diberikan.\n"
            "Gunakan struktur: judul, pendahuluan, isi (2-3 paragraf), kesimpulan.\n"
            "Gunakan bahasa Indonesia yang baik dan benar."
        )
