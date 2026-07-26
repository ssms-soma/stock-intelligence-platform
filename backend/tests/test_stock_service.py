import unittest
from unittest.mock import Mock

from app.services.stock_service import StockService


class StockServiceCacheTests(unittest.TestCase):
    def test_valid_stock_response_is_cached(self):
        service = StockService()
        service.stock_agent = Mock()
        service.stock_agent.get_stock_data.return_value = {
            "ticker": "AMZN",
            "current_price": 185.0,
            "previous_close": 182.0,
        }

        first = service.get_stock_data("amzn")
        second = service.get_stock_data("AMZN")

        self.assertEqual(first, second)
        service.stock_agent.get_stock_data.assert_called_once_with("AMZN")

    def test_all_null_warning_response_is_not_cached(self):
        service = StockService()
        service.stock_agent = Mock()
        service.stock_agent.get_stock_data.return_value = {
            "ticker": "AMZN",
            "current_price": None,
            "previous_close": None,
            "market_cap": None,
            "pe_ratio": None,
            "fifty_two_week_high": None,
            "fifty_two_week_low": None,
            "volume": None,
            "warning": "Stock data is temporarily unavailable.",
        }

        service.get_stock_data("AMZN")
        service.get_stock_data("AMZN")

        self.assertEqual(service.stock_agent.get_stock_data.call_count, 2)

    def test_empty_history_is_not_cached(self):
        service = StockService()
        service.stock_agent = Mock()
        service.stock_agent.get_stock_history.return_value = []

        service.get_stock_history("AMZN", "6mo")
        service.get_stock_history("AMZN", "6mo")

        self.assertEqual(service.stock_agent.get_stock_history.call_count, 2)


if __name__ == "__main__":
    unittest.main()
