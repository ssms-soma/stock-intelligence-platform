from fastapi import APIRouter
from pydantic import BaseModel

from app.services.sentiment_service import SentimentService


class SentimentRequest(BaseModel):
    text: str


router = APIRouter(tags=["Sentiment"])

sentiment_service = SentimentService()


@router.post("/sentiment")
def analyze_sentiment(request: SentimentRequest):
    result = sentiment_service.analyze_sentiment(request.text)

    return {"text": request.text, **result}
