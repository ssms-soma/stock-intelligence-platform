from app.agents.stock_data_agent import StockDataAgent


class StockService:
    def __init__(self):
        self.stock_agent = StockDataAgent()

    def get_stock_data(self, ticker: str):
        return self.stock_agent.get_stock_data(ticker)