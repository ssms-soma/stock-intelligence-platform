import unittest

from app.documents.index_store import DocumentIndexStore
from app.documents.models import LoadedDocument, LoadedDocumentUnit
from app.rag.models import RAGChunk
from app.rag.vector_store import InMemoryVectorStore
from app.services.document_service import DocumentService, DocumentServiceError


class FakeLoader:
    def __init__(self, extension=".txt"):
        self.extension = extension

    async def load(self, upload_file):
        return LoadedDocument(
            title="annual-report",
            extension=self.extension,
            content_type=(
                "application/pdf"
                if self.extension == ".pdf"
                else "text/plain"
            ),
            units=(
                [
                    LoadedDocumentUnit(
                        text="Revenue grew during the year.",
                        page=1,
                    ),
                    LoadedDocumentUnit(
                        text="Cloud services also grew.",
                        page=2,
                    ),
                ]
                if self.extension == ".pdf"
                else [
                    LoadedDocumentUnit(
                        text="Revenue grew during the year."
                    )
                ]
            ),
        )


class FakeRAGService:
    def __init__(self, index_warning=None, query_warning=None):
        self.index_warning = index_warning
        self.query_warning = query_warning
        self.query_calls = []

    def index_documents(self, documents):
        if self.index_warning:
            return {
                "vector_store": None,
                "chunks": [],
                "embedding_provider": "fake",
                "embedding_model": "fake-embedding",
                "warning": self.index_warning,
            }
        chunks = [
            RAGChunk(
                document_id=document.document_id,
                title=document.title,
                source_type=document.source_type,
                text=document.text,
                chunk_id=(
                    f"{document.document_id}:page:{document.page}:chunk:0"
                    if document.page is not None
                    else f"{document.document_id}:chunk:0"
                ),
                page=document.page,
            )
            for document in documents
        ]
        store = InMemoryVectorStore()
        store.add(chunks, [[1.0, 0.0] for chunk in chunks])
        return {
            "vector_store": store,
            "chunks": chunks,
            "embedding_provider": "fake",
            "embedding_model": "fake-embedding",
            "warning": None,
        }

    def query_index(self, **kwargs):
        self.query_calls.append(kwargs)
        document_id = kwargs["vector_store"]._entries[0][0].document_id
        sources = [
            {
                "document_id": document_id,
                "title": "annual-report",
                "chunk_id": f"{document_id}:chunk:0",
                "source_type": "uploaded_text",
                "page": None,
                "score": 1.0,
            }
        ]
        return {
            "answer": None if self.query_warning else "Revenue grew.",
            "query": kwargs["query"],
            "sources": sources,
            "metadata": {
                "model": "fake-chat",
                "embedding_model": "fake-embedding",
                "retrieval_k": kwargs["top_k"],
                "mode": kwargs["mode"],
            },
            "warning": self.query_warning,
        }


class DocumentServiceTests(unittest.IsolatedAsyncioTestCase):
    def _service(self, rag_service=None, extension=".txt"):
        return DocumentService(
            loader=FakeLoader(extension=extension),
            index_store=DocumentIndexStore(max_documents=2),
            rag_service=rag_service or FakeRAGService(),
        )

    async def test_successful_upload_indexes_and_stores_document(self):
        service = self._service()

        result = await service.upload_document(object())

        self.assertEqual(result["status"], "indexed")
        self.assertEqual(result["chunks_indexed"], 1)
        self.assertEqual(result["embedding_model"], "fake-embedding")
        self.assertIn("process memory", result["warning"])
        self.assertIsNotNone(service.index_store.get(result["document_id"]))
        self.assertNotIn("pages_indexed", result)

    async def test_pdf_upload_preserves_pages_and_source_type(self):
        service = self._service(extension=".pdf")

        result = await service.upload_document(object())
        stored = service.index_store.get(result["document_id"])

        self.assertEqual(result["source_type"], "uploaded_pdf")
        self.assertEqual(result["pages_indexed"], 2)
        self.assertEqual(stored.pages_indexed, 2)
        chunks = [entry[0] for entry in stored.vector_store._entries]
        self.assertEqual([chunk.page for chunk in chunks], [1, 2])
        self.assertIn(":page:1:chunk:0", chunks[0].chunk_id)

    async def test_embedding_failure_does_not_store_document(self):
        service = self._service(FakeRAGService("Embeddings unavailable."))

        result = await service.upload_document(object())

        self.assertEqual(result["status"], "not_indexed")
        self.assertEqual(result["warning"], "Embeddings unavailable.")
        self.assertEqual(len(service.index_store), 0)

    async def test_pdf_embedding_failure_does_not_store_document(self):
        service = self._service(
            FakeRAGService("Embeddings unavailable."),
            extension=".pdf",
        )

        result = await service.upload_document(object())

        self.assertEqual(result["status"], "not_indexed")
        self.assertEqual(result["source_type"], "uploaded_pdf")
        self.assertEqual(result["pages_indexed"], 2)
        self.assertEqual(len(service.index_store), 0)

    async def test_successful_ask_and_llm_failure_preserve_sources(self):
        rag_service = FakeRAGService()
        service = self._service(rag_service)
        upload = await service.upload_document(object())

        result = service.ask_document(upload["document_id"], "Growth?", 3)
        self.assertEqual(result["answer"], "Revenue grew.")
        self.assertEqual(result["document_id"], upload["document_id"])
        self.assertEqual(result["metadata"]["mode"], "uploaded_document_rag")
        self.assertEqual(len(result["sources"]), 1)

        rag_service.query_warning = "Chat model unavailable."
        failed = service.ask_document(upload["document_id"], "Growth?", 3)
        self.assertIsNone(failed["answer"])
        self.assertEqual(len(failed["sources"]), 1)
        self.assertEqual(failed["warning"], "Chat model unavailable.")

    async def test_unknown_document_raises_structured_service_error(self):
        service = self._service()

        with self.assertRaises(DocumentServiceError) as raised:
            service.ask_document("missing", "Question", 2)

        self.assertEqual(raised.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
