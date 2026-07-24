import unittest
from unittest.mock import patch

from app.api.routes.search_routes import resolve_ticker


class SearchRoutesTests(unittest.TestCase):
    def test_route_delegates_to_resolver_service(self):
        expected = {
            "query": "Infosys",
            "resolved": True,
            "ticker": "INFY.NS",
        }

        with patch(
            "app.api.routes.search_routes.ticker_resolver_service.resolve",
            return_value=expected,
        ) as mock_resolve:
            result = resolve_ticker("Infosys")

        self.assertEqual(result, expected)
        mock_resolve.assert_called_once_with("Infosys")

    def test_route_returns_structured_unresolved_blank_response(self):
        result = resolve_ticker("")

        self.assertFalse(result["resolved"])
        self.assertIsNone(result["ticker"])
        self.assertIn("warning", result)

    def test_route_returns_structured_unresolved_unknown_response(self):
        result = resolve_ticker("some unknown company")

        self.assertFalse(result["resolved"])
        self.assertIsNone(result["ticker"])
        self.assertIn("warning", result)


if __name__ == "__main__":
    unittest.main()
