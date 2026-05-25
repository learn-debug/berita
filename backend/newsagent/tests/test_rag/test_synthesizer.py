import pytest

from newsagent.rag.synthesizer import Synthesizer


class FakeLLM:
    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        return "Ringkasan terstruktur tentang topik."

    async def complete_structured(
        self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048
    ) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


@pytest.mark.asyncio
async def test_synthesizer_returns_summary() -> None:
    llm = FakeLLM()
    s = Synthesizer(llm=llm)
    result = await s.synthesize(["doc1", "doc2"], "test topic")
    assert result != ""
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_synthesizer_empty_docs() -> None:
    llm = FakeLLM()
    s = Synthesizer(llm=llm)
    result = await s.synthesize([], "empty topic")
    assert result != ""
