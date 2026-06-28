from fastapi import APIRouter

from app.services.research_service import ResearchService


router = APIRouter(tags=["Research"])

research_service = ResearchService()


@router.get("/research/{ticker}")
def get_research_report(ticker: str):
    return research_service.get_research_report(ticker)
