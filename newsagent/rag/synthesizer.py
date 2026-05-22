import logging

from newsagent.llm.base_adapter import BaseLLMAdapter

logger = logging.getLogger(__name__)


class Synthesizer:
    def __init__(self, llm: BaseLLMAdapter) -> None:
        self.llm = llm

    async def synthesize(self, documents: list[str], topic: str) -> str:
        return await self.llm.complete(
            system="Sintesis dokumen-dokumen berikut menjadi ringkasan terstruktur "
            "yang relevan dengan topik.",
            prompt=f"Topik: {topic}\n\nDokumen:\n" + "\n---\n".join(documents),
        )
