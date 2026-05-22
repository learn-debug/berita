import logging

from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, llm: BaseLLMAdapter) -> None:
        self.llm = llm
        self._search = WebSearchTool()

    async def retrieve(self, topic: str) -> list[str]:
        documents: list[str] = []

        try:
            queries_text = await self.llm.complete(
                system="Kamu adalah asisten riset. "
                "Buat 3 query pencarian web yang spesifik untuk riset topik berita.",
                prompt=f"Topik: {topic}\n\nKembalikan 3 query, satu per baris, tanpa nomor atau bullet.",
            )
            queries = [q.strip() for q in queries_text.strip().split("\n") if q.strip()]

            for query in queries[:3]:
                try:
                    search_url = (
                        f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
                    )
                    page = await self._search.fetch_page(search_url)
                    if page and len(page) > 200:
                        documents.append(f"Sumber ({query}):\n{page}")
                except Exception as e:
                    logger.debug(
                        "[Retriever] fetch gagal untuk query '%s': %s", query, e
                    )

        except Exception as e:
            logger.error("[Retriever] error: %s", e)

        if not documents:
            try:
                fallback = await self.llm.complete(
                    system="Kamu adalah asisten riset. "
                    "Berikan informasi faktual dan konteks yang relevan tentang topik berita berikut.",
                    prompt=f"Berikan informasi faktual terkini tentang topik ini:\n{topic}",
                )
                documents = [fallback]
            except Exception as e:
                logger.error("[Retriever] fallback gagal: %s", e)
                documents = [topic]

        logger.info("[Retriever] %d dokumen terkumpul", len(documents))
        return documents

    async def close(self) -> None:
        await self._search.close()
