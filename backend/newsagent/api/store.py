import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from newsagent.core.state import ArticleState, ArticleStatus
from newsagent.memory.engine import get_engine

logger = logging.getLogger(__name__)


def ensure_uuid(article_id: str) -> str:
    try:
        return str(uuid.UUID(article_id))
    except ValueError:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, article_id))


def map_row_to_state(row: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    # Ensure correct structure for ArticleState compatibility
    return {
        "article_id": row.get("article_id_str") or str(row.get("id")),
        "input_type": row.get("input_type"),
        "raw_input": row.get("raw_input") or "",
        "rag_context": row.get("rag_context") or "",
        "draft": row.get("draft") or "",
        "fact_check_report": json.loads(row.get("fact_check_report"))
        if isinstance(row.get("fact_check_report"), str)
        else (row.get("fact_check_report") or {}),
        "edited_draft": row.get("edited_draft") or "",
        "aggregated_article": row.get("aggregated_article") or "",
        "credibility_score": row.get("credibility_score") or 0.0,
        "status": row.get("status"),
        "revision_count": row.get("revision_count") or 0,
        "events": events,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


class ArticleStore:
    async def claim_for_processing(self, article_id: str, revision_count: int) -> bool:
        uid = ensure_uuid(article_id)
        engine = await get_engine()

        # 1. Check if existing article prevents processing
        existing = await engine.fetchrow(
            "SELECT status FROM articles WHERE article_id_str = $1 OR id = $2",
            article_id,
            uuid.UUID(uid),
        )
        if existing:
            cur = existing.get("status")
            if cur in (
                ArticleStatus.PUBLISHED.value,
                ArticleStatus.REJECTED.value,
                ArticleStatus.PROCESSING.value,
            ):
                return False

        # 2. Try to insert claim
        try:
            # We use the raw connection pool to execute the insert securely
            pool = await engine.pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO article_claims (article_id_str, revision_count) VALUES ($1, $2)",
                    article_id,
                    revision_count,
                )
            return True
        except Exception:
            # Unique violation or other DB error means already claimed
            return False

    async def release_claim(self, article_id: str, revision_count: int) -> None:
        engine = await get_engine()
        await engine.execute(
            "DELETE FROM article_claims WHERE article_id_str = $1 AND revision_count = $2",
            article_id,
            revision_count,
        )

    async def reset_stale_processing(self) -> int:
        engine = await get_engine()
        # Find all processing articles
        rows = await engine.fetch("SELECT id, article_id_str FROM articles WHERE status = 'processing'")
        count = 0
        now = datetime.now(timezone.utc)
        for r in rows:
            uid = r["id"]
            # Update status to failed
            await engine.execute(
                "UPDATE articles SET status = 'failed', updated_at = $1 WHERE id = $2",
                now,
                uid,
            )
            # Record stale_reset event
            await engine.execute(
                """
                INSERT INTO article_events (article_id, agent, action, detail, created_at)
                VALUES ($1, $2, $3, $4, $5)
                """,
                uid,
                "system",
                "stale_reset",
                "Crash recovery: stale processing reset to failed",
                now,
            )
            count += 1
        return count

    async def save(self, article_id: str, state: ArticleState | dict[str, Any]) -> None:
        uid = ensure_uuid(article_id)
        engine = await get_engine()
        now = datetime.now(timezone.utc)

        # Convert fact_check_report to JSON string if it is a dict
        report = state.get("fact_check_report") or {}
        if isinstance(report, dict):
            report_str = json.dumps(report)
        else:
            report_str = str(report)

        # We construct input_type check to be valid ENUM value
        input_type = state.get("input_type", "topic")
        if input_type not in ("topic", "draft", "url"):
            input_type = "topic"

        status = state.get("status", "pending")
        if status not in ("pending", "processing", "published", "review", "rejected", "failed"):
            status = "pending"

        # Check if row already exists to set created_at
        existing = await engine.fetchrow("SELECT created_at FROM articles WHERE id = $1", uuid.UUID(uid))
        created_at = existing["created_at"] if existing else now

        # Perform the UPSERT on the articles table
        await engine.execute(
            """
            INSERT INTO articles (
                id, article_id_str, input_type, raw_input, title, rag_context, draft,
                fact_check_report, edited_draft, aggregated_article, credibility_score,
                status, revision_count, created_at, updated_at
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            ON CONFLICT (id) DO UPDATE SET
                input_type = EXCLUDED.input_type,
                raw_input = EXCLUDED.raw_input,
                title = EXCLUDED.title,
                rag_context = EXCLUDED.rag_context,
                draft = EXCLUDED.draft,
                fact_check_report = EXCLUDED.fact_check_report,
                edited_draft = EXCLUDED.edited_draft,
                aggregated_article = EXCLUDED.aggregated_article,
                credibility_score = EXCLUDED.credibility_score,
                status = EXCLUDED.status,
                revision_count = EXCLUDED.revision_count,
                updated_at = EXCLUDED.updated_at
            """,
            uuid.UUID(uid),
            article_id,
            input_type,
            state.get("raw_input") or "",
            state.get("title") or state.get("raw_input")[:100] if state.get("raw_input") else "",
            state.get("rag_context") or "",
            state.get("draft") or "",
            report_str,
            state.get("edited_draft") or "",
            state.get("aggregated_article") or "",
            float(state.get("credibility_score") or 0.0),
            status,
            int(state.get("revision_count") or 0),
            created_at,
            now,
        )

        # Sync events
        events = state.get("events") or []
        if events:
            # Fetch existing events to avoid duplicates
            existing_events = await engine.fetch(
                "SELECT agent, action, detail FROM article_events WHERE article_id = $1",
                uuid.UUID(uid),
            )
            existing_set = {(e["agent"], e["action"], e["detail"]) for e in existing_events}

            for event in events:
                agent = event.get("agent") or "unknown"
                action = event.get("action") or "unknown"
                detail = event.get("detail") or ""
                t_str = event.get("timestamp")
                if t_str:
                    try:
                        timestamp = datetime.fromisoformat(t_str)
                    except Exception:
                        timestamp = now
                else:
                    timestamp = now

                if (agent, action, detail) not in existing_set:
                    await engine.execute(
                        """
                        INSERT INTO article_events (article_id, agent, action, detail, created_at)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        uuid.UUID(uid),
                        agent,
                        action,
                        detail,
                        timestamp,
                    )

    async def get(self, article_id: str) -> dict[str, Any] | None:
        uid = ensure_uuid(article_id)
        engine = await get_engine()
        row = await engine.fetchrow(
            "SELECT * FROM articles WHERE id = $1 OR article_id_str = $2",
            uuid.UUID(uid),
            article_id,
        )
        if not row:
            return None

        # Fetch events
        event_rows = await engine.fetch(
            "SELECT agent, action, detail, created_at"
            " FROM article_events"
            " WHERE article_id = $1"
            " ORDER BY created_at ASC",
            row["id"],
        )
        events = [
            {
                "agent": e["agent"],
                "action": e["action"],
                "detail": e["detail"] or "",
                "timestamp": e["created_at"].isoformat(),
            }
            for e in event_rows
        ]

        return map_row_to_state(row, events)

    async def delete(self, article_id: str) -> bool:
        uid = ensure_uuid(article_id)
        engine = await get_engine()
        res = await engine.execute(
            "DELETE FROM articles WHERE id = $1 OR article_id_str = $2",
            uuid.UUID(uid),
            article_id,
        )
        # asyncpg execute returns a string like 'DELETE 1' or 'DELETE 0'
        return "DELETE 1" in res

    async def list(
        self,
        status: str | None = None,
        min_score: float | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> dict[str, Any]:
        engine = await get_engine()
        where_clauses = []
        params = []

        if status:
            params.append(status)
            where_clauses.append(f"status = ${len(params)}")

        if min_score is not None:
            params.append(min_score)
            where_clauses.append(f"credibility_score >= ${len(params)}")

        where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # Count total
        count_query = f"SELECT COUNT(*) FROM articles {where_sql}"
        total = await engine.fetchval(count_query, *params)

        # Fetch paginated rows
        offset = (page - 1) * limit
        params.append(limit)
        limit_param = f"${len(params)}"
        params.append(offset)
        offset_param = f"${len(params)}"

        select_query = f"""
            SELECT * FROM articles
            {where_sql}
            ORDER BY updated_at DESC
            LIMIT {limit_param} OFFSET {offset_param}
        """
        rows = await engine.fetch(select_query, *params)

        articles = []
        for r in rows:
            # We can skip fetching events for the list endpoint for speed, or return empty list
            articles.append(map_row_to_state(r, []))

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "articles": articles,
        }
