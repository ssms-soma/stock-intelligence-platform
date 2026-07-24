import unittest

from app.rag.models import RAGChunk
from app.rag.vector_store import InMemoryVectorStore


class InMemoryVectorStoreTests(unittest.TestCase):
    def setUp(self):
        self.first = RAGChunk("one", "One", "sample", "first", "one:chunk:0")
        self.second = RAGChunk("two", "Two", "sample", "second", "two:chunk:0")

    def test_ranks_by_cosine_similarity_and_limits_results(self):
        store = InMemoryVectorStore()
        store.add([self.first, self.second], [[1.0, 0.0], [0.0, 1.0]])

        results = store.search([0.9, 0.1], top_k=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].chunk.document_id, "one")
        self.assertGreater(results[0].score, 0.9)

    def test_rejects_count_and_dimension_mismatches(self):
        store = InMemoryVectorStore()

        with self.assertRaises(ValueError):
            store.add([self.first], [])

        store.add([self.first], [[1.0, 0.0]])
        with self.assertRaises(ValueError):
            store.add([self.second], [[1.0]])

        with self.assertRaises(ValueError):
            store.search([1.0], top_k=1)

    def test_zero_vector_similarity_is_safe(self):
        store = InMemoryVectorStore()
        store.add([self.first], [[0.0, 0.0]])

        result = store.search([1.0, 0.0], top_k=1)

        self.assertEqual(result[0].score, 0.0)


if __name__ == "__main__":
    unittest.main()
