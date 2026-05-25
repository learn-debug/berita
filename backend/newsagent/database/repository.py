from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from newsagent.core.state import ArticleState, ArticleStatus
from newsagent.memory.engine import get_engine

logger = logging.getLogger(__name__)


class ArticleRepository:
    def __init__(self) -> None:
        self._claimed: set[tuple[str, int]] = set()
        self._lock = asyncio.Lock()

    async def claim_for_processing(self, article_id: str, revision_count: int) -> bool:
        async with self._lock:
            key = (article_id, revision_count)
            if key in self._claimed:
                return False
            engine = await get_engine()
            row = await engine.fetchrow("SELECT status FROM articles WHERE id = $1", article_id)
            if row and row["status"] in (
                ArticleStatus.PUBLISHED.value,
                ArticleStatus.REJECTED.value,
                ArticleStatus.PROCESSING.value,
            ):
                return False
            self._claimed.add(key)
            return True

    async def release_claim(self, article_id: str, revision_count: int) -> None:
        self._claimed.discard((article_id, revision_count))

    async def reset_stale_processing(self) -> int:
        engine = await get_engine()
        result = await engine.execute("UPDATE articles SET status = 'failed' WHERE status = 'processing'")
        if result and result.startswith("UPDATE "):
            try:
                return int(result.split()[1])
            except (IndexError, ValueError):
                pass
        return 0

    async def save(self, article_id: str, state: ArticleState | dict[str, Any]) -> None:
        engine = await get_engine()
        existing = await engine.fetchrow("SELECT 1 FROM articles WHERE id = $1", article_id)

        params = (
            article_id,
            state.get("input_type", "topic"),
            state.get("raw_input", ""),
            state.get("title"),
            state.get("rag_context", ""),
            state.get("draft", ""),
            json.dumps(state.get("fact_check_report", {})),
            state.get("edited_draft", ""),
            state.get("aggregated_article", ""),
            float(state.get("credibility_score", 0.0)),
            state.get("status", "pending"),
            int(state.get("revision_count", 0)),
            state.get("published_title"),
            state.get("published_body"),
            state.get("published_url"),
        )

        if existing:
            await engine.execute(
                """
                UPDATE articles SET
                    input_type = $2, raw_input = $3, title = $4,
                    rag_context = $5, draft = $6,
                    fact_check_report = $7::jsonb,
                    edited_draft = $8, aggregated_article = $9,
                    credibility_score = $10, status = $11,
                    revision_count = $12,
                    published_title = $13, published_body = $14,
                    published_url = $15
                WHERE id = $1
                """,
                *params,
            )
        else:
            await engine.execute(
                """
                INSERT INTO articles (
                    id, input_type, raw_input, title,
                    rag_context, draft, fact_check_report,
                    edited_draft, aggregated_article,
                    credibility_score, status, revision_count,
                    published_title, published_body, published_url
                ) VALUES ($1, $2, $3, $4, $5, $6, $7::jsonb,
                          $8, $9, $10, $11, $12, $13, $14, $15)
                """,
                *params,
            )

    async def get(self, article_id: str) -> dict[str, Any] | None:
        engine = await get_engine()
        row = await engine.fetchrow("SELECT * FROM articles WHERE id = $1", article_id)
        if not row:
            return None
        return self._row_to_dict(row)

    async def delete(self, article_id: str) -> bool:
        engine = await get_engine()
        result = await engine.execute("DELETE FROM articles WHERE id = $1", article_id)
        return bool(result and "DELETE 1" in result)

    async def list(
        self,
        status: str | None = None,
        min_score: float | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        engine = await get_engine()

        conditions: list[str] = []
        params: list[Any] = []
        idx = 1

        if status:
            conditions.append(f"status = ${idx}")
            params.append(status)
            idx += 1
        if min_score is not None:
            conditions.append(f"credibility_score >= ${idx}")
            params.append(min_score)
            idx += 1

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        total = await engine.fetchval(f"SELECT COUNT(*) FROM articles {where_clause}", *params) or 0

        offset = (page - 1) * limit
        params.extend([limit, offset])
        rows = await engine.fetch(
            f"SELECT * FROM articles {where_clause} ORDER BY created_at DESC LIMIT ${idx} OFFSET ${idx + 1}",
            *params,
        )

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "articles": [self._row_to_dict(r) for r in rows],
        }

    def _row_to_dict(self, row: dict[str, Any]) -> dict[str, Any]:
        d = dict(row)
        for json_field in ("fact_check_report",):
            if isinstance(d.get(json_field), str):
                try:
                    d[json_field] = json.loads(d[json_field])
                except (json.JSONDecodeError, TypeError):
                    pass
        return d
