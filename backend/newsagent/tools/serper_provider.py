import logging

import httpx

from newsagent.tools.search_provider import SearchProvider

logger = logging.getLogger(__name__)


class SerperSearchProvider(SearchProvider):
    BASE_URL = "https://google.serper.dev/search"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15.0)
        return self._client

    async def search(self, query: str, max_results: int = 5) -> list[str]:
        try:
            client = await self._get_client()
            response = await client.post(
                self.BASE_URL,
                json={"q": query, "num": max_results},
                headers={"X-API-KEY": self._api_key, "Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

            documents: list[str] = []
            for r in data.get("organic", [])[:max_results]:
                snippet = r.get("snippet", "")
                url = r.get("link", "")
                if snippet:
                    documents.append(f"Sumber ({url}):\n{snippet}")
            logger.info(
                "[SerperSearchProvider] %d dokumen dari '%s'",
                len(documents),
                query,
            )
            return documents
        except Exception as e:
            logger.error("[SerperSearchProvider] search gagal: %s", e)
            return []

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
