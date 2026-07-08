from app.agents.news_agent import NewsAgent
from app.services.sentiment_service import SentimentService


class NewsService:
    def __init__(self):
        self.news_agent = NewsAgent()
        self.sentiment_service = SentimentService()
        self.last_warning = None

    def get_stock_news(self, query: str, page_size: int = 10):
        result = self.news_agent.get_stock_news(query, page_size)
        articles = result.get("articles", []) if isinstance(result, dict) else result
        self.last_warning = result.get("warning") if isinstance(result, dict) else None

        for article in articles:
            title = article.get("title") or ""
            description = article.get("description") or ""
            sentiment_text = f"{title} {description}"

            sentiment = self.sentiment_service.analyze_sentiment(sentiment_text)

            article["sentiment"] = sentiment["sentiment"]
            article["polarity"] = sentiment["polarity"]

        return articles
