from app.agents.research_agent import ResearchAgent
from app.services.news_service import NewsService
from app.services.stock_service import StockService


class ResearchService:
    def __init__(self):
        self.stock_service = StockService()
        self.news_service = NewsService()
        self.research_agent = ResearchAgent()

    def get_research_report(self, ticker: str):
        warnings = []
        stock_data = self.stock_service.get_stock_data(ticker)
        history_data = self.stock_service.get_stock_history(ticker, period="1mo")

        if stock_data.get("warning"):
            warnings.append(stock_data["warning"])

        if not history_data:
            warnings.append("Price history is unavailable or empty for this ticker.")

        news_query = stock_data.get("company_name") or ticker
        news_data = self.news_service.get_stock_news(news_query, page_size=5)

        if self.news_service.last_warning:
            warnings.append(self.news_service.last_warning)

        research_summary = self.research_agent.generate_research_summary(
            stock_data=stock_data,
            history_data=history_data,
            news_data=news_data,
        )
        market_metadata = self._get_market_metadata(stock_data)
        research_summary["market_metadata"] = market_metadata
        if warnings:
            research_summary["warnings"] = warnings

        response = {
            "stock_data": stock_data,
            "news_data": news_data,
            "market_metadata": market_metadata,
            "research_summary": research_summary,
        }

        if warnings:
            response["warnings"] = warnings

        return response

    def _get_market_metadata(self, stock_data):
        return {
            "market": stock_data.get("market"),
            "country": stock_data.get("country"),
            "exchange": stock_data.get("exchange"),
            "currency": stock_data.get("currency"),
            "currency_symbol": stock_data.get("currency_symbol"),
        }
