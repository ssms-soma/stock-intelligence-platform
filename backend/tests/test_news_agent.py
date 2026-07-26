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
        ]

        result = NewsAgent().get_stock_news("stock market", 5)

        self.assertEqual(result["articles"], [])
        self.assertIsNone(result["warning"])
        self.assertEqual(mock_get.call_count, 2)


if __name__ == "__main__":
    unittest.main()
