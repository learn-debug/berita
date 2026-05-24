import pytest

from newsagent.core.state import ArticleState
from newsagent.rag.pipeline import RAGPipeline


class FakeLLMRAG:
    def __init__(self) -> None:
        self.call_count = 0

    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        self.call_count += 1
        if self.call_count == 1:
            return "query 1\nquery 2\nquery 3"
        return "Ringkasan hasil sintesis."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


@pytest.mark.asyncio
async def test_rag_pipeline_sets_rag_context() -> None:
    llm = FakeLLMRAG()
    pipeline = RAGPipeline(llm=llm)

    state: ArticleState = {
        "article_id": "rag-test",
        "input_type": "topic",
        "raw_input": "Dampak AI terhadap media",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }

    result = await pipeline.run(state)

    assert result["rag_context"] != ""
    assert len(result["events"]) == 1
    assert result["events"][0]["agent"] == "RAGPipeline"


@pytest.mark.asyncio
async def test_rag_pipeline_fallback_on_error() -> None:
    class BrokenLLM:
        async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
            raise RuntimeError("API error")

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    pipeline = RAGPipeline(llm=llm)

    state: ArticleState = {
        "article_id": "rag-fail",
        "input_type": "topic",
        "raw_input": "Topik gagal",
        "rag_context": "",
        "draft": "",
        "fact_check_report": {},
        "edited_draft": "",
        "aggregated_article": "",
        "credibility_score": 0.0,
        "status": "processing",
        "events": [],
    }

    result = await pipeline.run(state)

    assert result["rag_context"] != ""
    assert "Topik gagal" in result["rag_context"]
    assert len(result["events"]) == 1


@pytest.mark.asyncio
async def test_rag_pipeline_close() -> None:
    llm = FakeLLMRAG()
    pipeline = RAGPipeline(llm=llm)

    await pipeline.close()
