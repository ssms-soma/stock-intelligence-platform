import math

from app.rag.models import RAGChunk, RetrievalResult


class InMemoryVectorStore:
    def __init__(self):
        self._entries: list[tuple[RAGChunk, list[float]]] = []
        self._dimensions: int | None = None

    def add(self, chunks: list[RAGChunk], embeddings: list[list[float]]):
        if len(chunks) != len(embeddings):
            raise ValueError("Chunk and embedding counts must match.")

        for chunk, embedding in zip(chunks, embeddings):
            self._validate_vector(embedding)
            self._entries.append((chunk, embedding))

    def search(self, query_embedding: list[float], top_k: int):
        self._validate_vector(query_embedding)
        limit = max(0, int(top_k))
        if limit == 0:
            return []

        results = [
            RetrievalResult(
                chunk=chunk,
                score=self._cosine_similarity(query_embedding, embedding),
            )
            for chunk, embedding in self._entries
        ]
        results.sort(key=lambda result: result.score, reverse=True)
        return results[:limit]

    def _validate_vector(self, vector):
        if not isinstance(vector, list) or not vector:
            raise ValueError("Embedding vectors must be non-empty lists.")

        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            for value in vector
        ):
            raise ValueError("Embedding vectors must contain finite numbers.")

        if self._dimensions is None:
            self._dimensions = len(vector)
        elif len(vector) != self._dimensions:
            raise ValueError("Embedding vector dimensions must match.")

    @staticmethod
    def _cosine_similarity(left, right):
        dot_product = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))

        if left_norm == 0 or right_norm == 0:
            return 0.0

        return dot_product / (left_norm * right_norm)
