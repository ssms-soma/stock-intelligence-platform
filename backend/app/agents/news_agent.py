import os
from datetime import datetime, timezone
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
            return self._get_yahoo_news(query, page_size)

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
            return self._get_yahoo_news(query, page_size)

        articles = response.json().get("articles", [])

        if not articles:
            return self._get_yahoo_news(query, page_size)

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

    def _get_yahoo_news(self, query: str, page_size: int):
        try:
            response = requests.get(
                "https://query1.finance.yahoo.com/v1/finance/search",
                params={
                    "q": query,
                    "quotesCount": 0,
                    "newsCount": page_size,
                },
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10,
            )
            response.raise_for_status()
            articles = response.json().get("news") or []
        except (requests.RequestException, ValueError):
            return {
                "articles": [],
                "warning": "News providers are temporarily unavailable.",
            }

        return {
            "articles": [
                {
                    "title": article.get("title"),
                    "source": article.get("publisher"),
                    "url": article.get("link"),
                    "published_at": self._format_timestamp(
                        article.get("providerPublishTime")
                    ),
                    "description": article.get("summary"),
                }
                for article in articles[:page_size]
                if article.get("title") and article.get("link")
            ],
            "warning": None,
        }

    def _format_timestamp(self, timestamp):
        try:
            return datetime.fromtimestamp(
                int(timestamp),
                tz=timezone.utc,
            ).isoformat()
        except (TypeError, ValueError, OSError):
            return None
