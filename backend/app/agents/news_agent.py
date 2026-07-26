import os
from pathlib import Path

import requests
from dotenv import load_dotenv


BACKEND_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(BACKEND_ENV_PATH)


class NewsAgent:
    """
    Handles stock news retrieval from NewsAPI.
    """

    def get_stock_news(self, query: str, page_size: int = 10):
        api_key = os.getenv("NEWS_API_KEY")

        if not api_key:
            return {
                "articles": [],
                "warning": "NEWS_API_KEY is not configured. News data is unavailable.",
            }

        try:
            response = requests.get(
                "https://newsapi.org/v2/everything",
                params={
                    "q": query,
                    "pageSize": page_size,
                    "sortBy": "publishedAt",
                    "language": "en",
                    "apiKey": api_key,
                },
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException:
            return {
                "articles": [],
                "warning": "NewsAPI is temporarily unavailable.",
            }

        articles = response.json().get("articles", [])

        return {
            "articles": [
                {
                    "title": article.get("title"),
                    "source": article.get("source", {}).get("name"),
                    "url": article.get("url"),
                    "published_at": article.get("publishedAt"),
                    "description": article.get("description"),
                }
                for article in articles
            ],
            "warning": None,
        }
