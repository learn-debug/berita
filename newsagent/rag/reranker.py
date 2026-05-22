class Reranker:
    def rerank(self, documents: list[str], query: str) -> list[str]:
        return sorted(documents, key=lambda d: len(set(d.split()) & set(query.split())), reverse=True)
