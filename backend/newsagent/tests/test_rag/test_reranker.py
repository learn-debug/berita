from newsagent.rag.reranker import Reranker


def test_reranker_empty_docs() -> None:
    r = Reranker()
    result = r.rerank([], "test query")
    assert result == []


def test_reranker_sorts_by_overlap() -> None:
    r = Reranker()
    docs = [
        "tentang berita politik terbaru",
        "olahraga sepak bola liga inggris",
        "politik pemilu presiden 2025",
    ]
    result = r.rerank(docs, "politik pemilu")
    assert result[0] == "politik pemilu presiden 2025"
    assert "tentang berita politik terbaru" in result
    assert "olahraga sepak bola liga inggris" in result


def test_reranker_preserves_all_docs() -> None:
    r = Reranker()
    docs = ["a b c", "d e f", "g h i"]
    result = r.rerank(docs, "a b")
    assert len(result) == 3
    assert set(result) == set(docs)


def test_reranker_single_doc() -> None:
    r = Reranker()
    result = r.rerank(["only document"], "query")
    assert result == ["only document"]


def test_reranker_query_with_only_stop_words() -> None:
    r = Reranker()
    docs = ["Doc A", "Doc B"]
    result = r.rerank(docs, "a in the di dan dari")
    assert result == docs
