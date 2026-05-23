import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.cost.token_budget import with_budget
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class DraftAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    @with_budget(max_tokens=4000)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[DraftAgent] mulai — article_id=%s", state["article_id"])

        try:
            result = await self.llm.complete(
                system=self._system_prompt(),
                prompt=PromptHardener.wrap_user_input(
                    f"Topik: {state['raw_input']}\n\nKonteks RAG:\n{state['rag_context']}"
                ),
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
