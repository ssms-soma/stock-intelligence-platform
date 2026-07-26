from dataclasses import dataclass
from datetime import datetime

from app.rag.vector_store import InMemoryVectorStore


@dataclass(frozen=True)
class LoadedDocument:
    title: str
    extension: str
    content_type: str
    text: str


@dataclass
class IndexedDocument:
    document_id: str
    title: str
    source_type: str
    extension: str
    content_type: str
    character_count: int
    chunk_count: int
    embedding_provider: str | None
    embedding_model: str | None
    created_at: datetime
    vector_store: InMemoryVectorStore
