import httpx
from bs4 import BeautifulSoup

from newsagent.tools.base import BaseTool


class WebSearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Fetch web page content from a given URL"

    async def setup(self) -> None:
        self._client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)

    async def fetch_page(self, url: str) -> str:
        if not hasattr(self, "_client"):
            await self.setup()
        response = await self._client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:5000]

    async def search(self, query: str) -> str:
        search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
        return await self.fetch_page(search_url)

    async def close(self) -> None:
        if hasattr(self, "_client"):
            await self._client.aclose()
