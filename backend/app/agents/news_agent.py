import os

import requests
from dotenv import load_dotenv


load_dotenv()


class NewsAgent:
    """
    Handles stock news retrieval from NewsAPI.
    """

    def get_stock_news(self, query: str, page_size: int = 10):
        api_key = os.getenv("NEWS_API_KEY")

        if not api_key:
            raise ValueError("NEWS_API_KEY environment variable is not set")

        response = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "pageSize": page_size,
                "sortBy": "publishedAt",
                "apiKey": api_key,
            },
            timeout=10,
        )
        response.raise_for_status()

        articles = response.json().get("articles", [])

        return [
            {
                "title": article.get("title"),
                "source": article.get("source", {}).get("name"),
                "url": article.get("url"),
                "published_at": article.get("publishedAt"),
                "description": article.get("description"),
            }
            for article in articles
        ]
