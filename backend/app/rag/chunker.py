from app.rag.models import RAGChunk, RAGDocument


class TextChunker:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = max(1, int(chunk_size))
        self.chunk_overlap = min(
            max(0, int(chunk_overlap)),
            self.chunk_size - 1,
        )

    def chunk_documents(self, documents: list[RAGDocument]):
        chunks = []
        for document in documents:
            chunks.extend(self.chunk_document(document))
        return chunks

    def chunk_document(self, document: RAGDocument):
        text = self._normalize_text(document.text)
        if not text:
            return []

        chunks = []
        step = self.chunk_size - self.chunk_overlap

        for index, start in enumerate(range(0, len(text), step)):
            chunk_text = text[start : start + self.chunk_size].strip()
            if not chunk_text:
                continue

            chunks.append(
                RAGChunk(
                    document_id=document.document_id,
                    title=document.title,
                    source_type=document.source_type,
                    text=chunk_text,
                    chunk_id=f"{document.document_id}:chunk:{index}",
                    page=document.page,
                    metadata=dict(document.metadata),
                )
            )

            if start + self.chunk_size >= len(text):
                break

        return chunks

    @staticmethod
    def _normalize_text(text):
        return " ".join(text.split()) if isinstance(text, str) else ""
