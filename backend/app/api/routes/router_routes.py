from fastapi import APIRouter

from app.agents.recommendation_agent import RecommendationAgent
from app.agents.router_agent import RouterAgent
from app.services.company_service import CompanyService
from app.services.news_service import NewsService
from app.services.recommendation_service import RecommendationService
from app.services.research_service import ResearchService
from app.services.stock_service import StockService


router = APIRouter(tags=["Router"])

stock_service = StockService()
company_service = CompanyService()
news_service = NewsService()
research_service = ResearchService()
recommendation_agent = RecommendationAgent()
recommendation_service = RecommendationService()

router_agent = RouterAgent(
    stock_service=stock_service,
    company_service=company_service,
    news_service=news_service,
    research_service=research_service,
    recommendation_agent=recommendation_agent,
    recommendation_service=recommendation_service,
)


@router.get("/router/{ticker}")
def route_stock_intent(ticker: str, intent: str = "research"):
    return router_agent.route(ticker=ticker, intent=intent)
