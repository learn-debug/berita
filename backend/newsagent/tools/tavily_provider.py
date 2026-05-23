import logging

from tavily import AsyncTavilyClient

from newsagent.tools.search_provider import SearchProvider

logger = logging.getLogger(__name__)


class TavilySearchProvider(SearchProvider):
    def __init__(self, api_key: str) -> None:
        self._client = AsyncTavilyClient(api_key=api_key)

    async def search(self, query: str, max_results: int = 5) -> list[str]:
        try:
            response = await self._client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_raw_content="markdown",
            )
            results = response.get("results", [])
            documents = []
            for r in results:
                content = r.get("raw_content") or r.get("content", "")
                if content:
                    source = r.get("url", "")
                    documents.append(f"Sumber ({source}):\n{content}")
            logger.info(
                "[TavilySearchProvider] %d dokumen dari '%s'",
                len(documents),
                query,
            )
            return documents
        except Exception as e:
            logger.error("[TavilySearchProvider] search gagal: %s", e)
            return []

    async def close(self) -> None:
        await self._client.close()
