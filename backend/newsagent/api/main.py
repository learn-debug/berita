import asyncio
import logging
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from newsagent.api.event_bus import EventBus
from newsagent.api.routers.articles import router as articles_router
from newsagent.api.routers.ws import router as ws_router
from newsagent.api.schemas import ArticleResponse, ProcessRequest
from newsagent.api.store import ArticleStore
from newsagent.core.state import ArticleState
from newsagent.security.input_sanitizer import InputSanitizer
from newsagent.security.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

_cleanup_handlers: list[Callable[[], Awaitable[None]]] = []
_graph: Any = None
_store: ArticleStore = ArticleStore()
_event_bus: EventBus = EventBus()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    from newsagent.core.graph import build_graph

    global _graph
    _graph = build_graph(cleanup_handlers=_cleanup_handlers, event_bus=_event_bus)

    yield

    for handler in _cleanup_handlers:
        try:
            await handler()
        except Exception as e:
            logger.warning("[cleanup] error: %s", e)


app = FastAPI(title="NewsAgent API", version="0.2.0", lifespan=lifespan)

app.include_router(articles_router)
app.include_router(ws_router)

limiter = RateLimiter(max_calls=60, window=60.0)


@app.post("/process")
async def process_article(req: ProcessRequest) -> ArticleResponse:
    if not await limiter.acquire():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        validated = InputSanitizer.validate_input_type(
            {"input_type": req.input_type, "raw_input": req.raw_input}
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    initial: ArticleState = {
        "article_id": uuid4().hex[:12],
        "input_type": validated["input_type"],
        "raw_input": validated["raw_input"],
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }

    if _graph is None:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    try:
        result = await asyncio.wait_for(_graph.ainvoke(initial), timeout=120.0)
        return ArticleResponse(article_id=result["article_id"], status=result["status"])
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Pipeline timeout")
    except Exception as e:
        logger.error("[API] pipeline error: %s", e)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
