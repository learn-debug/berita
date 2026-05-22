import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.resilience.retry_policy import with_retry
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.utils.prompt_loader import load_prompt

logger = logging.getLogger(__name__)


class EditorAgent:
    def __init__(self, llm: BaseLLMAdapter):
        self.llm = llm

    @with_retry(max_attempts=3)
    async def run(self, state: ArticleState) -> ArticleState:
        logger.info("[EditorAgent] mulai — article_id=%s", state["article_id"])

        try:
            prompt = PromptHardener.wrap_user_input(
                f"Berikut adalah draf artikel yang perlu diedit:\n\n{state['draft']}"
            )
            result = await self.llm.complete(
                system=self._system_prompt(),
                prompt=prompt,
            )
            edited = result
        except Exception as e:
            logger.error("[EditorAgent] gagal: %s", e)
            edited = state["draft"]

        return {
            **state,
            "edited_draft": edited,
            "events": state["events"]
            + [make_event("EditorAgent", "edit_draft", f"draf diedit ({len(edited)} chars)")],
        }

    def _system_prompt(self) -> str:
        return PromptHardener.SYSTEM_GUARD + "\n\n" + load_prompt("editor_agent.md")
