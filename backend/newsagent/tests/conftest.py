import asyncio
from typing import Any

import pytest

from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter

_cleanup_tasks: set[asyncio.Task] = set()


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


@pytest.fixture(autouse=True)
def clean_database():
    try:
        from newsagent.memory.engine import get_engine

        async def _truncate():
            engine = await get_engine()
            await engine.execute(
                "TRUNCATE TABLE article_claims, agent_costs, article_events, articles CASCADE"
            )

        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                # In active async tests, run it on the active loop
                task = loop.create_task(_truncate())
                _cleanup_tasks.add(task)
            else:
                loop.run_until_complete(_truncate())
        except RuntimeError:
            asyncio.run(_truncate())
    except Exception:
        pass
    return
