STOP_WORDS: set[str] = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "as",
    "and", "or", "but", "not", "so", "if", "it", "its", "this", "that",
    "these", "those", "i", "you", "he", "she", "we", "they",
    "dan", "di", "ke", "dari", "dengan", "untuk", "adalah", "ini", "itu",
    "yang", "dan", "di", "dari", "dengan", "pada", "dalam", "tidak", "akan",
}


class Reranker:
    def rerank(self, documents: list[str], query: str) -> list[str]:
        query_words = {w.lower() for w in query.split() if w.lower() not in STOP_WORDS}
        if not query_words:
            return documents
        return sorted(
            documents,
            key=lambda d: len(set(w.lower() for w in d.split() if w.lower() not in STOP_WORDS) & query_words),
            reverse=True,
        )
