from __future__ import annotations

from enum import StrEnum
from typing import Any, NotRequired, TypedDict

from newsagent.core.events import EventDict


class ArticleStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    REVIEW = "review"
    REVISION = "revision"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    FAILED = "failed"


_VALID_TRANSITIONS: dict[ArticleStatus, set[ArticleStatus]] = {
    ArticleStatus.PENDING: {ArticleStatus.PROCESSING},
    ArticleStatus.PROCESSING: {
        ArticleStatus.REVIEW,
        ArticleStatus.REVISION,
        ArticleStatus.PUBLISHED,
        ArticleStatus.FAILED,
    },
    ArticleStatus.REVIEW: {
        ArticleStatus.APPROVED,
        ArticleStatus.REJECTED,
        ArticleStatus.PROCESSING,
        ArticleStatus.PUBLISHED,
    },
    ArticleStatus.REVISION: {ArticleStatus.PROCESSING},
    ArticleStatus.APPROVED: {ArticleStatus.PUBLISHED},
    ArticleStatus.REJECTED: set(),
    ArticleStatus.PUBLISHED: set(),
    ArticleStatus.FAILED: {ArticleStatus.PROCESSING},
}


def transition_allowed(current: str | ArticleStatus, target: str | ArticleStatus) -> bool:
    if isinstance(current, str):
        try:
            current = ArticleStatus(current)
        except ValueError:
            return True
    if isinstance(target, str):
        try:
            target = ArticleStatus(target)
        except ValueError:
            return True
    allowed = _VALID_TRANSITIONS.get(current, set())
    return target in allowed


class FactCheckReport(TypedDict, total=False):
    claims: str
    queries: str
    evidence: str
    verdict: str
    verdict_raw: list[dict[str, Any]]


class ArticleState(TypedDict):
    article_id: str
    input_type: str
    raw_input: str
    rag_context: str
    draft: str
    fact_check_report: FactCheckReport
    edited_draft: str
    title: NotRequired[str]
    aggregated_article: str
    credibility_score: float
    status: str
    revision_count: int
    events: list[EventDict]
    published_title: NotRequired[str]
    published_body: NotRequired[str]
    published_url: NotRequired[str | None]
