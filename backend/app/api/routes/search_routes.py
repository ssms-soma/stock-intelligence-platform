from fastapi import APIRouter

from app.services.ticker_resolver_service import TickerResolverService


router = APIRouter(tags=["Search"])

ticker_resolver_service = TickerResolverService()


@router.get("/search/resolve")
def resolve_ticker(query: str = ""):
    return ticker_resolver_service.resolve(query)
