import httpx


class CMSClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )

    async def publish(self, title: str, content: str, status: str = "publish") -> dict:
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
        await self._client.aclose()
