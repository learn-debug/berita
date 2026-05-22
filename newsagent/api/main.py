import asyncio
import logging
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from newsagent.core.graph import build_graph
from newsagent.core.state import ArticleState
from newsagent.security.input_sanitizer import InputSanitizer
from newsagent.security.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

_cleanup_handlers: list[Callable[[], Awaitable[None]]] = []


@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    for handler in _cleanup_handlers:
        try:
            await handler()
        except Exception as e:
            logger.warning("[cleanup] error: %s", e)


app = FastAPI(title="NewsAgent API", version="0.1.0", lifespan=lifespan)

graph = build_graph()

limiter = RateLimiter(max_calls=60, window=60.0)


class ProcessRequest(BaseModel):
    input_type: str = "topic"
    raw_input: str


class ArticleResponse(BaseModel):
    article_id: str
    status: str


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

    try:
        result = await asyncio.wait_for(graph.ainvoke(initial), timeout=120.0)
        return ArticleResponse(article_id=result["article_id"], status=result["status"])
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Pipeline timeout")
    except Exception as e:
        logger.error("[API] pipeline error: %s", e)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
