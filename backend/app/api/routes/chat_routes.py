from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.chat_service import ChatService


class ChatDocumentRequest(BaseModel):
    document_id: str
    title: str
    source_type: str
    text: str
    page: int | None = None
    metadata: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    message: str
    ticker: str | None = None
    mode: str = "auto"
    documents: list[ChatDocumentRequest] = Field(default_factory=list)
    top_k: int | None = None


router = APIRouter(tags=["Chat"])

chat_service = ChatService()


@router.post("/chat")
def chat(request: ChatRequest):
    return chat_service.chat(
        message=request.message,
        ticker=request.ticker,
        mode=request.mode,
        documents=[document.model_dump() for document in request.documents],
        top_k=request.top_k,
    )
