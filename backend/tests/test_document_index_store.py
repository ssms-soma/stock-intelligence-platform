import unittest
from datetime import datetime, timezone

from app.documents.index_store import (
    DocumentIndexStore,
    DocumentIndexStoreFullError,
)
from app.documents.models import IndexedDocument
from app.rag.vector_store import InMemoryVectorStore


def indexed_document(document_id):
    return IndexedDocument(
        document_id=document_id,
        title="Report",
        source_type="uploaded_text",
        extension=".txt",
        content_type="text/plain",
        character_count=8,
        chunk_count=1,
        embedding_provider="fake",
        embedding_model="fake-model",
        created_at=datetime.now(timezone.utc),
        vector_store=InMemoryVectorStore(),
    )


class DocumentIndexStoreTests(unittest.TestCase):
    def test_adds_and_gets_document(self):
        store = DocumentIndexStore(max_documents=2)
        document = indexed_document("doc-1")

        self.assertIs(store.add(document), document)
        self.assertIs(store.get("doc-1"), document)
        self.assertEqual(len(store), 1)
        self.assertTrue(store.has_capacity())

    def test_rejects_new_document_when_full(self):
        store = DocumentIndexStore(max_documents=1)
        store.add(indexed_document("doc-1"))

        with self.assertRaises(DocumentIndexStoreFullError):
            store.add(indexed_document("doc-2"))

        self.assertFalse(store.has_capacity())
        self.assertIsNone(store.get("doc-2"))


if __name__ == "__main__":
    unittest.main()
