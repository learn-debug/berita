import logging

import httpx
from bs4 import BeautifulSoup

from newsagent.tools.search_provider import SearchProvider

logger = logging.getLogger(__name__)


class WebSearchTool(SearchProvider):
    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)
        return self._client

    async def search(self, query: str, max_results: int = 5) -> list[str]:
        search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
        try:
            client = await self._get_client()
            response = await client.get(
                search_url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; NewsAgent/1.0)"},
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            documents: list[str] = []

            for result in soup.select(".result__body")[:max_results]:
                snippet_el = result.select_one(".result__snippet")
                url_el = result.select_one(".result__url")
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                url = url_el.get_text(strip=True) if url_el else ""
                if snippet:
                    documents.append(f"Sumber ({url}):\n{snippet}")

            if documents:
                logger.info("[WebSearchTool] %d hasil dari DuckDuckGo", len(documents))
                return documents

            logger.warning("[WebSearchTool] no structured results, fallback to raw text")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            text = soup.get_text(separator="\n", strip=True)[:5000]
            return [f"Sumber ({search_url}):\n{text}"] if text else []

        except Exception as e:
            logger.error("[WebSearchTool] search gagal: %s", e)
            return []

    async def fetch_page(self, url: str) -> str:
        return await self._fetch_page(url)

    async def _fetch_page(self, url: str) -> str:
        client = await self._get_client()
        response = await client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:5000]

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
