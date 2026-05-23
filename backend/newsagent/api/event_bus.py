import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = {}

    def subscribe(self, article_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._queues.setdefault(article_id, []).append(q)
        return q

    def unsubscribe(self, article_id: str, q: asyncio.Queue) -> None:
        if article_id in self._queues:
            self._queues[article_id] = [x for x in self._queues[article_id] if x is not q]
            if not self._queues[article_id]:
                del self._queues[article_id]

    async def publish(self, article_id: str, event: dict[str, Any]) -> None:
        for q in self._queues.get(article_id, []):
            await q.put(event)
