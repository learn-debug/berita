import logging

from newsagent.tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self) -> None:
        self._search = WebSearchTool()

    async def retrieve(self, topic: str) -> list[str]:
        results = ["search: " + topic]
        return results

    async def close(self) -> None:
        await self._search.close()
