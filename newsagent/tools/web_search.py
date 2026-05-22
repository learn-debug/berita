import httpx
from bs4 import BeautifulSoup


class WebSearchTool:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(timeout=15.0, follow_redirects=True)

    async def fetch_page(self, url: str) -> str:
        response = await self._client.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:5000]

    async def close(self) -> None:
        await self._client.aclose()
