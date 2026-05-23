import pytest

from newsagent.tools.search_provider import SearchProvider


class ConcreteProvider(SearchProvider):
    async def search(self, query: str, max_results: int = 5) -> list[str]:
        return ["result"]


@pytest.mark.asyncio
async def test_close_default_noop() -> None:
    provider = ConcreteProvider()
    await provider.close()
