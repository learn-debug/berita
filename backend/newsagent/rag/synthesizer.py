import logging

from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.security.prompt_hardening import PromptHardener

logger = logging.getLogger(__name__)


class Synthesizer:
    def __init__(self, llm: BaseLLMAdapter) -> None:
        self.llm = llm

    async def synthesize(self, documents: list[str], topic: str) -> str:
        max_doc_chars = 3000
        truncated: list[str] = []
        for d in documents:
            if len(d) > max_doc_chars:
                truncated.append(d[:max_doc_chars] + "\n[...truncated]")
            else:
                truncated.append(d)
        system = (
            PromptHardener.SYSTEM_GUARD
            + "\n\n"
            + "Sintesis dokumen-dokumen berikut menjadi ringkasan terstruktur "
            "yang relevan dengan topik."
        )
        docs_text = "\n---\n".join(truncated)
        user_prompt = PromptHardener.wrap_user_input(f"Topik: {topic}\n\nDokumen:\n" + docs_text)
        return await self.llm.complete(
            system=system,
            prompt=user_prompt,
            max_tokens=2048,
        )
