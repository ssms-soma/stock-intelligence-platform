from fastapi import APIRouter

from app.services.stock_service import StockService

router = APIRouter(tags=["Stocks"])

stock_service = StockService()


@router.get("/stocks/{ticker}")
def get_stock_data(ticker: str):
    return stock_service.get_stock_data(ticker)