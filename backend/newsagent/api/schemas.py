from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    input_type: str = Field(default="topic", pattern=r"^(topic|draft|url)$")
    raw_input: str = Field(min_length=1, max_length=10000)


class ArticleResponse(BaseModel):
    article_id: str
    status: str


class ArticleListItem(BaseModel):
    article_id: str
    title: str
    status: str
    credibility_score: float
    word_count: int
    revision_count: int = 0
    created_at: datetime | None = None
    published_url: str | None = None


class ArticleListResponse(BaseModel):
    total: int
    page: int
    limit: int
    articles: list[ArticleListItem]


class ArticleDetailResponse(BaseModel):
    article_id: str
    title: str
    content: str
    status: str
    credibility_score: float
    revision_count: int = 0
    fact_check_report: dict[str, Any]
    events: list[dict[str, Any]]
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PatchRequest(BaseModel):
    action: str  # approve | reject | retry
    content: str | None = None


class ProcessResponse(BaseModel):
    article_id: str
    status: str = "processing"
    message: str = "Pipeline started"
