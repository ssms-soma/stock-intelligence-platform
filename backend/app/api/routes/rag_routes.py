from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.rag_service import RAGService


class RAGDocumentRequest(BaseModel):
    document_id: str
    title: str
    source_type: str
    text: str
    page: int | None = None
    metadata: dict = Field(default_factory=dict)


class RAGTestRequest(BaseModel):
    query: str
    documents: list[RAGDocumentRequest] = Field(default_factory=list)
    top_k: int | None = None


router = APIRouter(tags=["RAG"])

rag_service = RAGService()


@router.post("/rag/test")
def test_rag(request: RAGTestRequest):
    return rag_service.test_rag(
        query=request.query,
        documents=[document.model_dump() for document in request.documents],
        top_k=request.top_k,
    )
