import pytest

from newsagent.rag.retriever import Retriever


class FakeLLM:
    def __init__(self) -> None:
        self.call_count = 0

    async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
        self.call_count += 1
        if self.call_count == 1:
            return "query 1\nquery 2\nquery 3"
        return "Fallback information about the topic."

    async def complete_structured(
        self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048
    ) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


class FakeSearchProvider:
    def __init__(self) -> None:
        self.closed = False

    async def search(self, query: str, max_results: int = 5) -> list[str]:
        return [f"Sumber: hasil untuk '{query}'"]

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_retriever_returns_documents() -> None:
    llm = FakeLLM()
    retriever = Retriever(llm=llm, search_provider=FakeSearchProvider())

    docs = await retriever.retrieve("test topic")

    assert len(docs) > 0
    assert all(isinstance(d, str) for d in docs)


@pytest.mark.asyncio
async def test_retriever_handles_partial_fetch_failure() -> None:
    class PartiallyFailingSearch(FakeSearchProvider):
        def __init__(self) -> None:
            self.call_count = 0

        async def search(self, query: str, max_results: int = 5) -> list[str]:
            self.call_count += 1
            if self.call_count == 2:
                raise RuntimeError("search failed")
            return [f"Sumber: hasil untuk '{query}'"]

    llm = FakeLLM()
    retriever = Retriever(llm=llm, search_provider=PartiallyFailingSearch())

    docs = await retriever.retrieve("test topic")

    assert len(docs) >= 1


@pytest.mark.asyncio
async def test_retriever_llm_fallback_when_web_empty() -> None:
    class EmptySearch(FakeSearchProvider):
        async def search(self, query: str, max_results: int = 5) -> list[str]:
            return []

    llm = FakeLLM()
    retriever = Retriever(llm=llm, search_provider=EmptySearch())

    docs = await retriever.retrieve("test topic")

    assert len(docs) >= 1


@pytest.mark.asyncio
async def test_retriever_fallback_to_topic() -> None:
    class BrokenLLM:
        def __init__(self) -> None:
            self.call_count = 0

        async def complete(self, prompt: str, system: str | None = None, max_tokens: int = 2048) -> str:
            self.call_count += 1
            if self.call_count <= 2:
                raise RuntimeError("API error")
            return "fallback"

        async def complete_structured(
            self, prompt: str, schema: dict, system: str | None = None, max_tokens: int = 2048
        ) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    retriever = Retriever(llm=llm, search_provider=FakeSearchProvider())

    docs = await retriever.retrieve("topic fallback")

    assert len(docs) >= 1


@pytest.mark.asyncio
async def test_retriever_close() -> None:
    llm = FakeLLM()
    search = FakeSearchProvider()
    retriever = Retriever(llm=llm, search_provider=search)

    await retriever.close()
    assert search.closed
