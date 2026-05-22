from typing import TypedDict


class ArticleState(TypedDict):
    article_id: str
    input_type: str
    raw_input: str
    rag_context: str
    draft: str
    fact_check_report: dict
    edited_draft: str
    aggregated_article: str
    credibility_score: float
    status: str
    events: list[dict]
