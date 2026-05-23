import logging

from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.security.prompt_hardening import PromptHardener
from newsagent.tools.search_factory import search_provider_factory
from newsagent.tools.search_provider import SearchProvider

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, llm: BaseLLMAdapter, search_provider: SearchProvider | None = None) -> None:
        self.llm = llm
        self._search = search_provider or search_provider_factory()

    async def retrieve(self, topic: str) -> list[str]:
        documents: list[str] = []

        try:
            queries_text = await self.llm.complete(
                system=PromptHardener.SYSTEM_GUARD + "\n\n" + "Kamu adalah asisten riset. "
                "Buat 3 query pencarian web yang spesifik untuk riset topik berita.",
                prompt=PromptHardener.wrap_user_input(
                    f"Topik: {topic}\n\nKembalikan 3 query, satu per baris, tanpa nomor atau bullet."
                ),
            )
            queries = [q.strip() for q in queries_text.strip().split("\n") if q.strip()]

            for query in queries[:3]:
                try:
                    results = await self._search.search(query)
                    documents.extend(results)
                except Exception as e:
                    logger.warning("[Retriever] search gagal untuk query '%s': %s", query, e)

        except Exception as e:
            logger.error("[Retriever] error: %s", e)

        if not documents:
            try:
                fallback = await self.llm.complete(
                    system=PromptHardener.SYSTEM_GUARD + "\n\n" + "Kamu adalah asisten riset. "
                    "Berikan informasi faktual dan konteks yang relevan tentang topik berita berikut.",
                    prompt=PromptHardener.wrap_user_input(
                        f"Berikan informasi faktual terkini tentang topik ini:\n{topic}"
                    ),
                )
                documents = [fallback]
            except Exception as e:
                logger.error("[Retriever] fallback gagal: %s", e)
                documents = [topic]

        logger.info("[Retriever] %d dokumen terkumpul", len(documents))
        return documents

    async def close(self) -> None:
        await self._search.close()
