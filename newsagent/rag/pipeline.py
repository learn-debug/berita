import logging

from newsagent.core.events import make_event
from newsagent.core.state import ArticleState
from newsagent.llm.base_adapter import BaseLLMAdapter
from newsagent.rag.reranker import Reranker
from newsagent.rag.retriever import Retriever
from newsagent.rag.synthesizer import Synthesizer

logger = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self, llm: BaseLLMAdapter) -> None:
        self.llm = llm
        self.retriever = Retriever(llm=llm)
        self.reranker = Reranker()
        self.synthesizer = Synthesizer(llm=llm)

    async def run(self, state: ArticleState) -> ArticleState:
        article_id = state["article_id"]
        topic = state["raw_input"]
        logger.info("[RAGPipeline] mulai — article_id=%s", article_id)

        try:
            documents = await self.retriever.retrieve(topic)
            logger.info("[RAGPipeline] %d dokumen dari retriever", len(documents))

            reranked = self.reranker.rerank(documents, topic)
            top_k = reranked[:5]
            logger.info("[RAGPipeline] %d dokumen setelah rerank", len(top_k))

            summary = await self.synthesizer.synthesize(top_k, topic)
            logger.info("[RAGPipeline] sintesis selesai — %d karakter", len(summary))

            return {
                **state,
                "rag_context": summary,
                "events": state["events"]
                + [
                    make_event(
                        "RAGPipeline",
                        "rag_complete",
                        f"RAG selesai: {len(documents)} dok, {len(top_k)} top, {len(summary)} chars",
                    )
                ],
            }

        except Exception as e:
            logger.error("[RAGPipeline] gagal: %s", e)
            return {
                **state,
                "rag_context": f"Konteks tentang: {topic}",
                "events": state["events"]
                + [make_event("RAGPipeline", "failed", f"RAG pipeline error: {e}")],
            }

    async def close(self) -> None:
        await self.retriever.close()
