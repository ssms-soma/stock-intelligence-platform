from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.documents.loaders import DocumentLoadError
from app.services.document_service import DocumentService, DocumentServiceError


class DocumentAskRequest(BaseModel):
    question: str = Field(max_length=2_000)
    top_k: int | None = Field(default=None, ge=1, le=10)


router = APIRouter(tags=["Documents"])

document_service = DocumentService()


def _structured_error(status_code, warning):
    raise HTTPException(
        status_code=status_code,
        detail={
            "status": "rejected",
            "warning": warning,
        },
    )


@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        return await document_service.upload_document(file)
    except DocumentLoadError as error:
        _structured_error(error.status_code, error.warning)
    except DocumentServiceError as error:
        _structured_error(error.status_code, error.warning)


@router.post("/documents/{document_id}/ask")
def ask_document(document_id: str, request: DocumentAskRequest):
    try:
        return document_service.ask_document(
            document_id=document_id,
            question=request.question,
            top_k=request.top_k,
        )
    except DocumentServiceError as error:
        _structured_error(error.status_code, error.warning)
