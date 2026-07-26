from datetime import datetime, timezone
from uuid import uuid4

from app.config import settings
from app.documents.index_store import (
    DocumentIndexStore,
    DocumentIndexStoreFullError,
)
from app.documents.loaders import TextDocumentLoader
from app.documents.models import IndexedDocument
from app.rag.models import RAGDocument
from app.services.rag_service import RAGService


class DocumentServiceError(RuntimeError):
    def __init__(self, warning: str, status_code: int):
        super().__init__(warning)
        self.warning = warning
        self.status_code = status_code


class DocumentService:
    MEMORY_WARNING = (
        "This document index is stored in process memory and will be cleared "
        "when the backend restarts."
    )

    def __init__(self, loader=None, index_store=None, rag_service=None):
        self.loader = loader or TextDocumentLoader(
            max_bytes=settings.document_upload_max_bytes,
            max_characters=settings.document_text_max_chars,
        )
        self.index_store = index_store or DocumentIndexStore(
            max_documents=settings.document_index_max_documents,
        )
        self.rag_service = rag_service or RAGService()

    async def upload_document(self, upload_file):
        loaded = await self.loader.load(upload_file)
        if not self.index_store.has_capacity():
            raise DocumentServiceError(
                "The in-memory document index is full.",
                status_code=409,
            )

        document_id = uuid4().hex
        source_type = "uploaded_text"
        rag_document = RAGDocument(
            document_id=document_id,
            title=loaded.title,
            source_type=source_type,
            text=loaded.text,
            metadata={
                "extension": loaded.extension,
                "content_type": loaded.content_type,
            },
        )
        index_result = self.rag_service.index_documents([rag_document])

        if index_result["warning"] or not index_result["vector_store"]:
            return {
                "document_id": document_id,
                "title": loaded.title,
                "source_type": source_type,
                "chunks_indexed": 0,
                "embedding_model": index_result["embedding_model"],
                "status": "not_indexed",
                "warning": index_result["warning"]
                or "Document indexing is unavailable.",
            }

        indexed_document = IndexedDocument(
            document_id=document_id,
            title=loaded.title,
            source_type=source_type,
            extension=loaded.extension,
            content_type=loaded.content_type,
            character_count=len(loaded.text),
            chunk_count=len(index_result["chunks"]),
            embedding_provider=index_result["embedding_provider"],
            embedding_model=index_result["embedding_model"],
            created_at=datetime.now(timezone.utc),
            vector_store=index_result["vector_store"],
        )
        try:
            self.index_store.add(indexed_document)
        except DocumentIndexStoreFullError as error:
            raise DocumentServiceError(str(error), status_code=409) from error

        return {
            "document_id": document_id,
            "title": loaded.title,
            "source_type": source_type,
            "chunks_indexed": indexed_document.chunk_count,
            "embedding_model": indexed_document.embedding_model,
            "status": "indexed",
            "warning": self.MEMORY_WARNING,
        }

    def ask_document(self, document_id, question, top_k=None):
        normalized_document_id = (
            document_id.strip() if isinstance(document_id, str) else ""
        )
        indexed_document = self.index_store.get(normalized_document_id)
        if indexed_document is None:
            raise DocumentServiceError(
                "The requested uploaded document was not found.",
                status_code=404,
            )

        rag_result = self.rag_service.query_index(
            query=question,
            vector_store=indexed_document.vector_store,
            top_k=top_k,
            embedding_model=indexed_document.embedding_model,
            mode="uploaded_document_rag",
        )
        return {
            "answer": rag_result["answer"],
            "document_id": indexed_document.document_id,
            "sources": rag_result["sources"],
            "metadata": rag_result["metadata"],
            "warning": rag_result["warning"],
        }
