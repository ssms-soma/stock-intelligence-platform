from app.agents.research_agent import ResearchAgent
from app.services.news_service import NewsService
from app.services.stock_service import StockService


class ResearchService:
    def __init__(self):
        self.stock_service = StockService()
        self.news_service = NewsService()
        self.research_agent = ResearchAgent()

    def get_research_report(self, ticker: str):
        stock_data = self.stock_service.get_stock_data(ticker)
        history_data = self.stock_service.get_stock_history(ticker, period="1mo")

        news_query = stock_data.get("company_name") or ticker
        news_data = self.news_service.get_stock_news(news_query, page_size=5)

        research_summary = self.research_agent.generate_research_summary(
            stock_data=stock_data,
            history_data=history_data,
            news_data=news_data,
        )

        return {
            "stock_data": stock_data,
            "news_data": news_data,
            "research_summary": research_summary,
        }
