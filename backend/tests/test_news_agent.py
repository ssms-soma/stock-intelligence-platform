import unittest
from unittest.mock import Mock, patch

import requests

from app.agents.news_agent import NewsAgent


class NewsAgentTests(unittest.TestCase):
    @patch.dict("os.environ", {}, clear=True)
    @patch("app.agents.news_agent.requests.get")
    def test_uses_yahoo_when_news_api_key_is_missing(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "news": [
                {
                    "title": "Stocks rally on strong earnings",
                    "publisher": "Example",
                    "link": "https://example.com/article",
                    "providerPublishTime": 1753401600,
                }
            ]
        }
        mock_get.return_value = response

        result = NewsAgent().get_stock_news("stock market", 5)

        self.assertEqual(len(result["articles"]), 1)
        self.assertEqual(result["articles"][0]["source"], "Example")
        self.assertIsNone(result["warning"])

    @patch.dict("os.environ", {"NEWS_API_KEY": "test"}, clear=True)
    @patch("app.agents.news_agent.requests.get")
    def test_uses_yahoo_when_news_api_fails(self, mock_get):
        yahoo_response = Mock()
        yahoo_response.json.return_value = {"news": []}
        mock_get.side_effect = [
            requests.ConnectionError("unavailable"),
            yahoo_response,
            requests.ConnectionError("unavailable"),
            yahoo_response,
        ]

        result = NewsAgent().get_stock_news("stock market", 5)

        self.assertEqual(result["articles"], [])
        self.assertIn("Relevant news", result["warning"])
        self.assertEqual(mock_get.call_count, 4)

    def test_rejects_unrelated_apple_football_news(self):
        agent = NewsAgent()
        articles = [
            {
                "title": "Longview prepares for Apple Springs football game",
                "description": "The Tigers open their high-school season Friday.",
                "url": "https://example.test/sports",
            }
        ]

        self.assertEqual(
            agent._filter_relevant_articles(articles, "Apple Inc."),
            [],
        )

    def test_retains_genuine_apple_article(self):
        agent = NewsAgent()
        article = {
            "title": "Apple announces new iPhone manufacturing investment",
            "description": "Apple Inc. outlined its latest product plans.",
            "url": "https://example.test/apple",
        }

        self.assertEqual(
            agent._filter_relevant_articles([article], "Apple Inc."),
            [article],
        )

    def test_tcs_full_name_expands_to_common_aliases(self):
        candidates = NewsAgent()._query_candidates(
            "Tata Consultancy Services Limited"
        )

        self.assertIn("Tata Consultancy Services", candidates)
        self.assertIn("TCS", candidates)

    def test_tcs_short_name_article_is_relevant_to_full_name_query(self):
        agent = NewsAgent()
        article = {
            "title": "TCS reports stronger quarterly revenue",
            "description": "The technology company raised its outlook.",
        }

        self.assertEqual(
            agent._filter_relevant_articles(
                [article], "Tata Consultancy Services Limited"
            ),
            [article],
        )

    def test_wipro_full_name_expands_and_accepts_short_name_article(self):
        agent = NewsAgent()
        candidates = agent._query_candidates("Wipro Limited")
        article = {
            "title": "Wipro wins technology services contract",
            "description": "The company announced the agreement Tuesday.",
        }

        self.assertIn("Wipro", candidates)
        self.assertEqual(
            agent._filter_relevant_articles([article], "Wipro Limited"),
            [article],
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_alias_fallback_stops_after_relevant_news(self):
        agent = NewsAgent()
        empty = {"articles": [], "warning": None}
        relevant = {
            "articles": [
                {
                    "title": "TCS reports stronger quarterly revenue",
                    "description": "The company raised its outlook.",
                }
            ],
            "warning": None,
        }

        with patch.object(
            agent, "_get_yahoo_news", side_effect=[empty, relevant]
        ) as yahoo_news:
            result = agent.get_stock_news(
                "Tata Consultancy Services Limited", 5
            )

        self.assertEqual(result["articles"], relevant["articles"])
        self.assertEqual(yahoo_news.call_count, 2)

    @patch.dict("os.environ", {"NEWS_API_KEY": "test"}, clear=True)
    def test_general_market_query_uses_bounded_fallback(self):
        agent = NewsAgent()
        empty = {"articles": [], "warning": None}
        market_article = {
            "title": "Financial markets rise after inflation report",
            "description": "Stocks and bonds advanced.",
            "url": "https://example.test/markets",
        }
        with patch.object(
            agent,
            "_get_news_api_news",
            side_effect=[empty, empty],
        ), patch.object(
            agent,
            "_get_yahoo_news",
            side_effect=[empty, {"articles": [market_article], "warning": None}],
        ):
            result = agent.get_stock_news("stock market", 5)

        self.assertEqual(result["articles"], [market_article])

    @patch.dict("os.environ", {"NEWS_API_KEY": "test"}, clear=True)
    def test_unavailable_or_irrelevant_providers_return_safe_empty_list(self):
        agent = NewsAgent()
        irrelevant = {
            "articles": [{"title": "Tigers win football opener"}],
            "warning": None,
        }
        unavailable = {"articles": [], "warning": "unavailable"}
        with patch.object(agent, "_get_news_api_news", return_value=irrelevant), patch.object(
            agent, "_get_yahoo_news", return_value=unavailable
        ):
            result = agent.get_stock_news("Apple Inc.", 5)

        self.assertEqual(result["articles"], [])
        self.assertIn("Relevant news", result["warning"])


if __name__ == "__main__":
    unittest.main()
