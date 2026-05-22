from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from newsagent.core.graph import build_graph
from newsagent.core.state import ArticleState

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
    initial: ArticleState = {
        "article_id": uuid4().hex[:12],
        "input_type": req.input_type,
        "raw_input": req.raw_input,
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }
    result = await graph.ainvoke(initial)
    return ArticleResponse(article_id=result["article_id"], status=result["status"])
