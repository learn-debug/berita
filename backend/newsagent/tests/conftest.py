from typing import Any

import pytest

from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter


class FakeLLM(BaseLLMAdapter):
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return "Fake LLM response"

    async def complete_structured(
        self, prompt: str, schema: dict[str, Any], system: str | None = None
    ) -> dict[str, Any]:
        return {"raw": "fake structured response"}

    def model_name(self) -> str:
        return "fake"


@pytest.fixture
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture
def base_state() -> ArticleState:
    return ArticleState(
        article_id="test-123",
        input_type="topic",
        raw_input="Topik test",
        rag_context="Konteks dari RAG",
        draft="Ini adalah draft artikel untuk test.",
        fact_check_report={},
        edited_draft="",
        aggregated_article="",
        credibility_score=0.0,
        status="processing",
        revision_count=0,
        events=[],
    )
