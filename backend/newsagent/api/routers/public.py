import json
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from newsagent.api.store import ensure_uuid, map_row_to_state
from newsagent.memory.engine import get_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/public")


@router.get("/articles")
async def list_public_articles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    category: str | None = Query(None),
    sort: str = Query("latest", pattern=r"^(latest|score)$"),
    min_score: float | None = Query(None, ge=0.0, le=1.0),
) -> dict[str, Any]:
    engine = await get_engine()

    conditions = ["status = 'published'"]
    params: list[Any] = []

    if category:
        conditions.append("input_type = $" + str(len(params) + 2))
        params.append(category)

    if min_score is not None:
        conditions.append("credibility_score >= $" + str(len(params) + 2))
        params.append(min_score)

    where_sql = " AND ".join(conditions)
    count_sql = f"SELECT COUNT(*) FROM articles WHERE {where_sql}"
    total = await engine.fetchval(count_sql, *params)

    order = "created_at DESC" if sort == "latest" else "credibility_score DESC"
    offset = (page - 1) * limit
    select_sql = f"""
        SELECT * FROM articles
        WHERE {where_sql}
        ORDER BY {order}
        LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
    """
    rows = await engine.fetch(select_sql, *params, limit, offset)

    articles = []
    for r in rows:
        articles.append(_map_public_article(r))

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "articles": articles,
    }


@router.get("/articles/{article_id}")
async def get_public_article(article_id: str) -> dict[str, Any]:
    engine = await get_engine()
    uid = ensure_uuid(article_id)

    row = await engine.fetchrow(
        "SELECT * FROM articles WHERE (article_id_str = $1 OR id = $2) AND status = 'published'",
        article_id,
        uid,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Article not found")

    events = await engine.fetch(
        "SELECT * FROM article_events WHERE article_id = $1 ORDER BY created_at ASC",
        row["id"],
    )

    result = _map_public_article(row)
    result["events"] = [dict(e) for e in events]
    return result


@router.get("/categories")
async def list_categories() -> dict[str, Any]:
    engine = await get_engine()

    rows = await engine.fetch("""
        SELECT input_type, COUNT(*) as count
        FROM articles
        WHERE status = 'published'
        GROUP BY input_type
        ORDER BY count DESC
    """)

    categories = []
    for r in rows:
        categories.append({
            "slug": r["input_type"],
            "name": _category_name(r["input_type"]),
            "count": r["count"],
        })

    return {"categories": categories}


@router.get("/stats")
async def get_public_stats() -> dict[str, Any]:
    engine = await get_engine()

    total = await engine.fetchval(
        "SELECT COUNT(*) FROM articles WHERE status = 'published'"
    )
    avg_score = await engine.fetchval(
        "SELECT COALESCE(AVG(credibility_score), 0) FROM articles WHERE status = 'published'"
    )
    latest = await engine.fetchval(
        "SELECT MAX(created_at) FROM articles WHERE status = 'published'"
    )

    return {
        "total_articles": total,
        "avg_credibility_score": round(float(avg_score), 3) if avg_score else 0.0,
        "latest_article_at": latest.isoformat() if latest else None,
    }


def _map_public_article(row: dict[str, Any]) -> dict[str, Any]:
    title = row.get("published_title") or row.get("title") or row.get("raw_input", "")[:80]
    body = row.get("published_body") or row.get("aggregated_article") or row.get("edited_draft") or row.get("draft") or ""
    report_raw = row.get("fact_check_report")
    fact_check = report_raw if isinstance(report_raw, dict) else (
        json.loads(report_raw) if isinstance(report_raw, str) else {}
    )

    claims = []
    if fact_check and "verdict_raw" in fact_check:
        claims = fact_check["verdict_raw"]
    elif fact_check and "claims" in fact_check:
        claims = [{"claim": fact_check["claims"], "verdict": "unverified", "evidence": ""}]

    return {
        "id": str(row.get("id", "")),
        "article_id": row.get("article_id_str") or str(row.get("id", "")),
        "title": title,
        "body": body,
        "excerpt": body[:200] if body else "",
        "credibility_score": row.get("credibility_score") or 0.0,
        "category": _category_name(row.get("input_type", "topic")),
        "input_type": row.get("input_type", "topic"),
        "source_url": row.get("source_url"),
        "published_url": row.get("published_url"),
        "claims": claims,
        "revision_count": row.get("revision_count") or 0,
        "created_at": row.get("created_at").isoformat() if row.get("created_at") else None,
        "updated_at": row.get("updated_at").isoformat() if row.get("updated_at") else None,
    }


def _category_name(input_type: str) -> str:
    names = {
        "topic": "Topik Umum",
        "draft": "Artikel",
        "url": "Rangkuman Berita",
    }
    return names.get(input_type, input_type)
