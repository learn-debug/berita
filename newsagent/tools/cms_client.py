import httpx

from newsagent.tools.base import BaseTool


class CMSClient(BaseTool):
    @property
    def name(self) -> str:
        return "cms_client"

    @property
    def description(self) -> str:
        return "Publish articles to WordPress CMS"

    def __init__(self, base_url: str, api_key: str) -> None:
        self._base_url = base_url
        self._api_key = api_key

    async def setup(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=30.0,
        )

    async def publish(self, title: str, content: str, status: str = "publish") -> dict:
        if not hasattr(self, "_client"):
            await self.setup()
        response = await self._client.post(
            "/wp-json/wp/v2/posts",
            json={
                "title": title,
                "content": content,
                "status": status,
            },
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        if hasattr(self, "_client"):
            await self._client.aclose()
