import time
from typing import Any

from newsagent.core.state import ArticleState


class ArticleStore:
    def __init__(self) -> None:
        self._articles: dict[str, dict[str, Any]] = {}

    async def save(self, article_id: str, state: ArticleState) -> None:
        now = time.time()
        existing = self._articles.get(article_id, {})
        existing.update(dict(state))
        if "created_at" not in existing:
            existing["created_at"] = now
        existing["updated_at"] = now
        self._articles[article_id] = existing

    async def get(self, article_id: str) -> dict[str, Any] | None:
        return self._articles.get(article_id)

    async def delete(self, article_id: str) -> bool:
        return self._articles.pop(article_id, None) is not None

    async def list(
        self,
        status: str | None = None,
        min_score: float | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        items = list(self._articles.values())
        if status:
            items = [a for a in items if a.get("status") == status]
        if min_score is not None:
            items = [a for a in items if (a.get("credibility_score") or 0) >= min_score]
        items.sort(key=lambda a: a.get("updated_at", 0), reverse=True)
        total = len(items)
        start = (page - 1) * limit
        end = start + limit
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "articles": items[start:end],
        }
