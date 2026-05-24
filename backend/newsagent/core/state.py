from typing import Any, TypedDict

from typing_extensions import NotRequired

from newsagent.core.events import EventDict


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
    aggregated_article: str
    credibility_score: float
    status: str
    revision_count: int
    events: list[EventDict]
    published_title: NotRequired[str]
    published_body: NotRequired[str]
    published_url: NotRequired[str | None]
