from app.agents.news_agent import NewsAgent


class NewsService:
    def __init__(self):
        self.news_agent = NewsAgent()

    def get_stock_news(self, query: str, page_size: int = 10):
        return self.news_agent.get_stock_news(query, page_size)
