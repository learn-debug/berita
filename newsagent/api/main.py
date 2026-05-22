import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from newsagent.core.graph import build_graph
from newsagent.core.state import ArticleState
from newsagent.security.input_sanitizer import InputSanitizer
from newsagent.security.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

app = FastAPI(title="NewsAgent API", version="0.1.0")

graph = build_graph()


class ProcessRequest(BaseModel):
    input_type: str = "topic"
    raw_input: str


class ArticleResponse(BaseModel):
    article_id: str
    status: str


@app.post("/process")
async def process_article(req: ProcessRequest) -> ArticleResponse:
    limiter = RateLimiter(max_calls=60, window=60.0)
    if not limiter._allow():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        validated = InputSanitizer.validate_input_type({"input_type": req.input_type, "raw_input": req.raw_input})
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
        result = await graph.ainvoke(initial)
        return ArticleResponse(article_id=result["article_id"], status=result["status"])
    except Exception as e:
        logger.error("[API] pipeline error: %s", e)
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
