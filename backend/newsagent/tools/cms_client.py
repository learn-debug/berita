import httpx

from newsagent.security.input_sanitizer import InputSanitizer
from newsagent.tools.base import BaseTool


class CMSClient(BaseTool):
    @property
    def name(self) -> str:
        return "cms_client"

    @property
    def description(self) -> str:
        return "Publish articles to WordPress CMS"

    def __init__(self, base_url: str, api_key: str, client: httpx.AsyncClient | None = None) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._client = client

    async def setup(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=30.0,
            )

    async def publish(self, title: str, content: str, status: str = "publish") -> dict:
        client = self._client
        if client is None:
            await self.setup()
            client = self._client
        if client is None:
            raise RuntimeError("CMS client not initialized after setup")
        safe_title = InputSanitizer.sanitize(title)
        safe_content = InputSanitizer.sanitize(content)
        response = await client.post(
            "/wp-json/wp/v2/posts",
            json={
                "title": safe_title,
                "content": safe_content,
                "status": status,
            },
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        if hasattr(self, "_client") and self._client is not None:
            await self._client.aclose()
