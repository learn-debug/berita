import pytest

from newsagent.rag.retriever import Retriever


class FakeLLM:
    def __init__(self) -> None:
        self.call_count = 0

    async def complete(self, prompt: str, system: str | None = None) -> str:
        self.call_count += 1
        if self.call_count == 1:
            return "query 1\nquery 2\nquery 3"
        return "Fallback information about the topic."

    async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
        return {"raw": "test"}

    def model_name(self) -> str:
        return "fake"


class FakeSearch:
    def __init__(self) -> None:
        self.closed = False

    async def fetch_page(self, url: str) -> str:
        return "Some relevant web content for the query."

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_retriever_returns_documents() -> None:
    llm = FakeLLM()
    retriever = Retriever(llm=llm)
    retriever._search = FakeSearch()

    docs = await retriever.retrieve("test topic")

    assert len(docs) > 0
    assert all(isinstance(d, str) for d in docs)


@pytest.mark.asyncio
async def test_retriever_handles_partial_fetch_failure() -> None:
    class PartiallyFailingSearch:
        def __init__(self) -> None:
            self.call_count = 0

        async def fetch_page(self, url: str) -> str:
            self.call_count += 1
            if self.call_count == 2:
                raise RuntimeError("fetch failed")
            return "Some content for query."

        async def close(self) -> None:
            pass

    llm = FakeLLM()
    retriever = Retriever(llm=llm)
    retriever._search = PartiallyFailingSearch()

    docs = await retriever.retrieve("test topic")

    assert len(docs) >= 1


@pytest.mark.asyncio
async def test_retriever_llm_fallback_when_web_empty() -> None:
    class EmptySearch:
        async def fetch_page(self, url: str) -> str:
            return ""

        async def close(self) -> None:
            pass

    llm = FakeLLM()
    retriever = Retriever(llm=llm)
    retriever._search = EmptySearch()

    docs = await retriever.retrieve("test topic")

    assert len(docs) >= 1


@pytest.mark.asyncio
async def test_retriever_fallback_to_topic() -> None:
    class BrokenLLM:
        def __init__(self) -> None:
            self.call_count = 0

        async def complete(self, prompt: str, system: str | None = None) -> str:
            self.call_count += 1
            if self.call_count <= 2:
                raise RuntimeError("API error")
            return "fallback"

        async def complete_structured(self, prompt: str, schema: dict, system: str | None = None) -> dict:
            raise RuntimeError("API error")

        def model_name(self) -> str:
            return "broken"

    llm = BrokenLLM()
    retriever = Retriever(llm=llm)
    retriever._search = FakeSearch()

    docs = await retriever.retrieve("topic fallback")

    assert len(docs) >= 1


@pytest.mark.asyncio
async def test_retriever_close() -> None:
    llm = FakeLLM()
    retriever = Retriever(llm=llm)
    retriever._search = FakeSearch()

    await retriever.close()
