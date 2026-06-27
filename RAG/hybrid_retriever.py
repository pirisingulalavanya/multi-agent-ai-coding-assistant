from rank_bm25 import BM25Okapi
from RAG.vector_store import vector_store
from loguru import logger

class HybridRetriever:
    def __init__(self):
        self.bm25 = None

    def _build_bm25(self):
        if vector_store.chunks:
            tokenized = [chunk.lower().split() for chunk in vector_store.chunks]
            self.bm25 = BM25Okapi(tokenized)

    def retrieve(self, query: str, k: int = 4) -> str:
        if not vector_store.chunks:
            return ""

        self._build_bm25()

        # Dense retrieval (FAISS)
        dense_results = vector_store.search(query, k=k)

        # Sparse retrieval (BM25)
        sparse_results = []
        if self.bm25:
            tokenized_query = query.lower().split()
            scores = self.bm25.get_scores(tokenized_query)
            top_indices = sorted(
                range(len(scores)),
                key=lambda i: scores[i],
                reverse=True
            )[:k]
            sparse_results = [vector_store.chunks[i] for i in top_indices]

        # Combine and deduplicate
        seen = set()
        combined = []
        for chunk in dense_results + sparse_results:
            if chunk not in seen:
                seen.add(chunk)
                combined.append(chunk)

        context = "\n\n---\n\n".join(combined[:k])
        logger.info(f"Retrieved {len(combined)} chunks for query: {query[:50]}")
        return context

hybrid_retriever = HybridRetriever()