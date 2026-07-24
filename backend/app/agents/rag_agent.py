from app.rag.vector_store import InMemoryVectorStore


class RAGAgent:
    def retrieve(
        self,
        vector_store: InMemoryVectorStore,
        query_embedding: list[float],
        top_k: int,
    ):
        return vector_store.search(query_embedding, top_k)

    def build_sources(self, retrieval_results):
        return [
            {
                "document_id": result.chunk.document_id,
                "title": result.chunk.title,
                "chunk_id": result.chunk.chunk_id,
                "source_type": result.chunk.source_type,
                "page": result.chunk.page,
                "score": round(result.score, 4),
            }
            for result in retrieval_results
        ]

    def build_context(self, retrieval_results):
        return [
            {
                "document_id": result.chunk.document_id,
                "title": result.chunk.title,
                "chunk_id": result.chunk.chunk_id,
                "source_type": result.chunk.source_type,
                "page": result.chunk.page,
                "text": result.chunk.text,
            }
            for result in retrieval_results
        ]
