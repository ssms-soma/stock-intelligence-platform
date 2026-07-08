from fastapi import APIRouter

from app.services.recommendation_service import RecommendationService


router = APIRouter(tags=["Recommendations"])

recommendation_service = RecommendationService()


@router.get("/recommendations/{ticker}")
def get_recommendations(ticker: str):
    return recommendation_service.get_recommendations(ticker)
