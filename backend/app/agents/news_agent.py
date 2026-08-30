import os
import re
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
        queries = self._query_candidates(query)

        for candidate in queries:
            if api_key:
                result = self._get_news_api_news(candidate, page_size, api_key)
                relevant = self._filter_relevant_articles(
                    result["articles"], query
                )
                if relevant:
                    return {"articles": relevant[:page_size], "warning": None}

            result = self._get_yahoo_news(candidate, page_size)
            relevant = self._filter_relevant_articles(result["articles"], query)
            if relevant:
                return {"articles": relevant[:page_size], "warning": None}

        return {
            "articles": [],
            "warning": "Relevant news is temporarily unavailable.",
        }

    def _get_news_api_news(self, query, page_size, api_key):
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

    def _query_candidates(self, query):
        normalized = self._normalize(query)
        if normalized in {"stock market", "financial markets", "markets", "business"}:
            return [query, "financial markets"] if normalized != "financial markets" else [query]
        return [query]

    def _filter_relevant_articles(self, articles, original_query):
        return [
            article
            for article in articles
            if self._is_relevant(article, original_query)
        ]

    def _is_relevant(self, article, query):
        text = self._normalize(
            f"{article.get('title') or ''} {article.get('description') or ''}"
        )
        normalized_query = self._normalize(query)
        if not text:
            return False

        if normalized_query in {"stock market", "financial markets", "markets", "business"}:
            finance_terms = (
                "stock", "stocks", "market", "markets", "shares", "investor",
                "finance", "financial", "economy", "economic", "earnings",
                "nasdaq", "dow", "s&p", "bond", "fed", "inflation",
            )
            return any(self._has_phrase(text, term) for term in finance_terms)

        aliases = self._company_aliases(normalized_query)
        strong_aliases = aliases["strong"]
        ambiguous_aliases = aliases["ambiguous"]
        business_terms = (
            "stock", "stocks", "share", "shares", "company", "business",
            "earnings", "revenue", "profit", "investor", "ceo", "nasdaq",
            "nyse", "launch", "product", "technology", "manufacturing",
        )
        if any(self._has_phrase(text, alias) for alias in strong_aliases):
            return True
        return any(self._has_phrase(text, alias) for alias in ambiguous_aliases) and any(
            self._has_phrase(text, term) for term in business_terms
        )

    def _company_aliases(self, query):
        aliases = {
            "apple inc": ({"apple inc", "aapl", "iphone", "ipad", "macbook", "macos", "app store"}, {"apple"}),
            "aapl": ({"apple inc", "aapl", "iphone", "ipad", "macbook", "macos", "app store"}, {"apple"}),
            "microsoft": ({"microsoft", "msft", "windows", "azure", "xbox"}, set()),
            "microsoft corporation": ({"microsoft", "msft", "windows", "azure", "xbox"}, set()),
            "nvidia": ({"nvidia", "nvda", "geforce"}, set()),
            "reliance industries limited": ({"reliance industries", "reliance ns"}, {"reliance"}),
            "reliance ns": ({"reliance industries", "reliance ns"}, {"reliance"}),
        }
        strong, ambiguous = aliases.get(query, ({query}, set()))
        return {"strong": strong, "ambiguous": ambiguous}

    @staticmethod
    def _normalize(value):
        return " ".join(re.sub(r"[^a-z0-9&]+", " ", str(value or "").lower()).split())

    @staticmethod
    def _has_phrase(text, phrase):
        return bool(re.search(rf"\b{re.escape(phrase)}\b", text))

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
