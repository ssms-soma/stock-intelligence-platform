from fastapi import APIRouter

from app.services.stock_service import StockService

router = APIRouter(tags=["Stocks"])

stock_service = StockService()


@router.get("/stocks/{ticker}")
def get_stock_data(ticker: str):
    return stock_service.get_stock_data(ticker)


@router.get("/stocks/{ticker}/history")
def get_stock_history(ticker: str, period: str = "6mo"):
    return stock_service.get_stock_history(ticker, period)
