import asyncio
import logging
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from newsagent.api.auth import verify_api_key_or_jwt as verify_api_key
from newsagent.api.schemas import PatchRequest, ProcessRequest, ProcessResponse
from newsagent.core.state import ArticleState
from newsagent.security.input_sanitizer import InputSanitizer
from newsagent.security.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/articles")
limiter = RateLimiter(max_calls=60, window=60.0)


def _make_title(raw: str) -> str:
    return raw[:80] if raw else "Untitled"


@router.post("/process", status_code=202)
async def process_article(req: ProcessRequest, _auth: None = Depends(verify_api_key)) -> ProcessResponse:
    if not await limiter.acquire():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        validated = InputSanitizer.validate_input_type(
            {"input_type": req.input_type, "raw_input": req.raw_input}
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    from newsagent.api.main import _event_bus, _graph, _store

    article_id = uuid4().hex[:12]

    initial: ArticleState = {
        "article_id": article_id,
        "input_type": validated["input_type"],
        "raw_input": validated["raw_input"],
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "revision_count": 0,
        "events": [],
    }

    await _store.save(article_id, initial)
    await _event_bus.publish(
        article_id,
        {
            "type": "pipeline_start",
            "article_id": article_id,
            "message": "Pipeline started",
        },
    )

    asyncio.create_task(_run_pipeline(article_id, initial, _graph, _store, _event_bus))

    return ProcessResponse(article_id=article_id)


async def _run_pipeline(
    article_id: str,
    initial: ArticleState,
    graph: Any,
    store: Any,
    event_bus: Any,
) -> None:
    try:
        result = await asyncio.wait_for(graph.ainvoke(initial), timeout=120.0)
        status = result.get("status", "failed")
        await store.save(article_id, result)
        await event_bus.publish(
            article_id,
            {
                "type": "pipeline_complete",
                "article_id": article_id,
                "status": status,
            },
        )
    except asyncio.TimeoutError:
        await store.save(article_id, {"status": "failed"})
        await event_bus.publish(
            article_id,
            {
                "type": "pipeline_error",
                "article_id": article_id,
                "error": "Pipeline timeout after 120s",
            },
        )
    except Exception as e:
        logger.error("[pipeline] %s failed: %s", article_id, e)
        await store.save(article_id, {"status": "failed"})
        await event_bus.publish(
            article_id,
            {
                "type": "pipeline_error",
                "article_id": article_id,
                "error": str(e),
            },
        )


@router.get("")
async def list_articles(
    _auth: None = Depends(verify_api_key),
    status: str | None = Query(None),
    min_score: float | None = Query(None, ge=0.0, le=1.0),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    from newsagent.api.main import _store

    return await _store.list(status=status, min_score=min_score, page=page, limit=limit)


@router.get("/{article_id}")
async def get_article(article_id: str, _auth: None = Depends(verify_api_key)) -> dict:
    from newsagent.api.main import _store

    article = await _store.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.patch("/{article_id}")
async def patch_article(article_id: str, body: PatchRequest, _auth: None = Depends(verify_api_key)) -> dict:
    from newsagent.api.main import _store

    article = await _store.get(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    action = body.action
    if action == "approve":
        article["status"] = "approved"
    elif action == "reject":
        article["status"] = "rejected"
    elif action == "retry":
        article["status"] = "processing"
    else:
        raise HTTPException(status_code=422, detail=f"Unknown action: {action}")

    if body.content is not None:
        article["aggregated_article"] = body.content

    await _store.save(article_id, article)
    return article
