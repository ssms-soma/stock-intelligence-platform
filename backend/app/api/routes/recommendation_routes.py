from fastapi import APIRouter

from app.agents.recommendation_agent import RecommendationAgent


router = APIRouter(tags=["Recommendations"])

recommendation_agent = RecommendationAgent()


@router.get("/recommendations/{ticker}")
def get_recommendations(ticker: str):
    result = recommendation_agent.recommend_related_companies(ticker)
    recommendations = result.get("recommendations", [])

    response = {
        "ticker": result.get("ticker"),
        "recommendations": recommendations,
        "source": "rule_based",
    }

    if not recommendations:
        response["warning"] = "No recommendations found for this ticker."

    return response
