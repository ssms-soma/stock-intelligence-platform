from fastapi import APIRouter

from app.services.news_service import NewsService

router = APIRouter(tags=["News"])

news_service = NewsService()


@router.get("/news/{query}")
def get_stock_news(query: str, page_size: int = 10):
    return news_service.get_stock_news(query, page_size)
