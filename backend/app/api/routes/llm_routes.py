from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm_service import LLMService


class LLMTestRequest(BaseModel):
    prompt: str


router = APIRouter(tags=["LLM"])

llm_service = LLMService()


@router.get("/llm/status")
def get_llm_status():
    return llm_service.get_status()


@router.post("/llm/test")
def test_llm_prompt(request: LLMTestRequest):
    return llm_service.test_prompt(request.prompt)
