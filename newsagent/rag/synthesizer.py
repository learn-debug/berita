import logging

from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.security.prompt_hardening import PromptHardener

logger = logging.getLogger(__name__)


class Synthesizer:
    def __init__(self, llm: BaseLLMAdapter) -> None:
        self.llm = llm

    async def synthesize(self, documents: list[str], topic: str) -> str:
        return await self.llm.complete(
            system=PromptHardener.SYSTEM_GUARD + "\n\n" + "Sintesis dokumen-dokumen berikut menjadi ringkasan terstruktur "
            "yang relevan dengan topik.",
            prompt=PromptHardener.wrap_user_input(f"Topik: {topic}\n\nDokumen:\n" + "\n---\n".join(documents)),
        )
