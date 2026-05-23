import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.cost.token_budget import with_budget
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.memory.draft_memory import DraftMemory
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class DraftAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm
        self._draft_memory = DraftMemory()

    async def _build_few_shot(self, topic: str) -> str:
        try:
            examples = await self._draft_memory.find_best(topic, limit=2)
            if not examples:
                examples = await self._draft_memory.find_high_score(min_score=0.75, limit=2)
            if examples:
                parts = ["\n--- CONTOH ARTIKEL BERNILAI TINGGI ---"]
                for i, ex in enumerate(examples, 1):
                    parts.append(f"\nContoh {i} (skor {ex['credibility_score']}):")
                    parts.append(ex["draft"][:500])
                return "\n".join(parts)
        except Exception as e:
            logger.warning("[DraftAgent] few-shot memory gagal: %s", e)
        return ""

    @with_retry(max_attempts=3)
    @with_budget(max_tokens=4000)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[DraftAgent] mulai — article_id=%s", state["article_id"])

        try:
            few_shot = await self._build_few_shot(state["raw_input"])
            context = f"Topik: {state['raw_input']}\n\nKonteks RAG:\n{state['rag_context']}"
            if few_shot:
                context += few_shot

            result = await self.llm.complete(
                system=self._system_prompt(),
                prompt=PromptHardener.wrap_user_input(context),
            )
            draft = result
            logger.info("[DraftAgent] selesai — %d karakter", len(draft))
        except Exception as e:
            logger.error("[DraftAgent] gagal: %s", e)
            draft = state["raw_input"]

        return {
            **state,
            "draft": draft,
            "events": state["events"]
            + [make_event("DraftAgent", "generate_draft", f"draft selesai ({len(draft)} chars)")],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("draft_agent.md")
