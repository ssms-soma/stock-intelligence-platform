import unittest

from app.embeddings.base import EmbeddingResponse
from app.rag.chunker import TextChunker
from app.rag.models import RAGDocument
from app.services.rag_service import RAGService


class FakeEmbeddingProvider:
    model = "test-embedding-model"

    def __init__(self, warning=None):
        self.warning = warning

    def embed(self, texts):
        if self.warning:
            return EmbeddingResponse(
                embeddings=[],
                provider="fake",
                model=self.model,
                model_status="unavailable",
                warning=self.warning,
            )

        embeddings = []
        for text in texts:
            normalized = text.lower()
            embeddings.append(
                [1.0, 0.0] if "infosys" in normalized else [0.0, 1.0]
            )
        return EmbeddingResponse(
            embeddings=embeddings,
            provider="fake",
            model=self.model,
            model_status="available",
        )


class FakeLLMAgent:
    def __init__(self, warning=None):
        self.warning = warning
        self.calls = []

    def answer_question(self, question, context=None):
        self.calls.append((question, context))
        if self.warning:
            return {
                "response": "Unavailable",
                "model": "test-chat-model",
                "warning": self.warning,
            }
        return {
            "response": "Infosys provides consulting services.",
            "model": "test-chat-model",
        }


class RAGServiceTests(unittest.TestCase):
    def setUp(self):
        self.documents = [
            {
                "document_id": "infosys",
                "title": "Infosys overview",
                "source_type": "sample_text",
                "text": "Infosys provides consulting services.",
                "page": 1,
            },
            {
                "document_id": "tesla",
                "title": "Tesla overview",
                "source_type": "sample_text",
                "text": "Tesla manufactures electric vehicles.",
                "page": 1,
            },
        ]

    def _service(self, embedding_provider=None, llm_agent=None):
        return RAGService(
            embedding_provider=embedding_provider or FakeEmbeddingProvider(),
            llm_agent=llm_agent or FakeLLMAgent(),
            chunker=TextChunker(chunk_size=1000, chunk_overlap=0),
        )

    def test_runs_grounded_rag_flow_and_returns_sources(self):
        llm_agent = FakeLLMAgent()
        service = self._service(llm_agent=llm_agent)

        result = service.test_rag(
            "What does Infosys provide?",
            self.documents,
            top_k=1,
        )

        self.assertEqual(result["answer"], "Infosys provides consulting services.")
        self.assertEqual(result["sources"][0]["document_id"], "infosys")
        self.assertEqual(result["metadata"]["model"], "test-chat-model")
        self.assertEqual(
            result["metadata"]["embedding_model"],
            "test-embedding-model",
        )
        self.assertEqual(result["metadata"]["mode"], "rag_test")
        retrieved = llm_agent.calls[0][1]["retrieved_chunks"]
        self.assertEqual(retrieved[0]["document_id"], "infosys")

    def test_embedding_failure_prevents_ungrounded_generation(self):
        llm_agent = FakeLLMAgent()
        service = self._service(
            embedding_provider=FakeEmbeddingProvider("Embeddings unavailable."),
            llm_agent=llm_agent,
        )

        result = service.test_rag("Question", self.documents)

        self.assertIsNone(result["answer"])
        self.assertEqual(result["sources"], [])
        self.assertEqual(result["warning"], "Embeddings unavailable.")
        self.assertEqual(llm_agent.calls, [])

    def test_llm_failure_preserves_retrieved_sources(self):
        service = self._service(
            llm_agent=FakeLLMAgent("Chat model unavailable."),
        )

        result = service.test_rag("What does Infosys provide?", self.documents)

        self.assertIsNone(result["answer"])
        self.assertGreater(len(result["sources"]), 0)
        self.assertEqual(result["warning"], "Chat model unavailable.")

    def test_validates_blank_query_and_documents(self):
        service = self._service()

        blank_query = service.test_rag(" ", self.documents)
        no_documents = service.test_rag("Question", [])

        self.assertIn("query", blank_query["warning"])
        self.assertIn("document", no_documents["warning"])

    def test_reuses_index_for_uploaded_document_mode(self):
        service = self._service()
        rag_documents = [
            RAGDocument(
                document_id="infosys",
                title="Infosys overview",
                source_type="uploaded_text",
                text="Infosys provides consulting services.",
            )
        ]

        indexed = service.index_documents(rag_documents)
        result = service.query_index(
            query="What does Infosys provide?",
            vector_store=indexed["vector_store"],
            top_k=1,
            embedding_model=indexed["embedding_model"],
            mode="uploaded_document_rag",
        )

        self.assertIsNone(indexed["warning"])
        self.assertEqual(result["metadata"]["mode"], "uploaded_document_rag")
        self.assertEqual(result["sources"][0]["document_id"], "infosys")

    def test_page_aware_source_is_preserved(self):
        service = self._service()
        indexed = service.index_documents(
            [
                RAGDocument(
                    document_id="report",
                    title="Annual report",
                    source_type="uploaded_pdf",
                    text="Infosys reported revenue growth.",
                    page=12,
                )
            ]
        )

        result = service.query_index(
            query="What grew?",
            vector_store=indexed["vector_store"],
            top_k=1,
            embedding_model=indexed["embedding_model"],
        )

        self.assertEqual(result["sources"][0]["page"], 12)
        self.assertEqual(
            result["sources"][0]["chunk_id"],
            "report:page:12:chunk:0",
        )


if __name__ == "__main__":
    unittest.main()
