import unittest

from app.agents.rag_agent import RAGAgent
from app.rag.models import RAGChunk
from app.rag.vector_store import InMemoryVectorStore


class RAGAgentTests(unittest.TestCase):
    def test_returns_metadata_only_from_retrieved_chunks(self):
        chunk = RAGChunk(
            document_id="doc-1",
            title="Annual report",
            source_type="sample_text",
            text="Grounded evidence",
            chunk_id="doc-1:chunk:0",
            page=12,
        )
        store = InMemoryVectorStore()
        store.add([chunk], [[1.0, 0.0]])
        agent = RAGAgent()

        results = agent.retrieve(store, [1.0, 0.0], 1)
        sources = agent.build_sources(results)
        context = agent.build_context(results)

        self.assertEqual(
            sources[0],
            {
                "document_id": "doc-1",
                "title": "Annual report",
                "chunk_id": "doc-1:chunk:0",
                "source_type": "sample_text",
                "page": 12,
                "score": 1.0,
            },
        )
        self.assertEqual(context[0]["text"], "Grounded evidence")


if __name__ == "__main__":
    unittest.main()
