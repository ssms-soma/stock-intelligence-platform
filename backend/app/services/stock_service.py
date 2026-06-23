# Stock service layer
from app.agents.stock_data_agent import StockDataAgent


class StockService:
    def __init__(self):
        self.stock_agent = StockDataAgent()

    def get_stock_data(self, ticker: str):
        return self.stock_agent.get_stock_data(ticker)

    def get_stock_history(self, ticker: str, period: str = "6mo"):
        return self.stock_agent.get_stock_history(ticker, period)
