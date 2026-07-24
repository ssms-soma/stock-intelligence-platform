from dataclasses import dataclass, field


@dataclass
class RAGDocument:
    document_id: str
    title: str
    source_type: str
    text: str
    page: int | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class RAGChunk:
    document_id: str
    title: str
    source_type: str
    text: str
    chunk_id: str
    page: int | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class RetrievalResult:
    chunk: RAGChunk
    score: float
