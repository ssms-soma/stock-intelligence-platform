import json
import math
import unittest
from unittest.mock import Mock, patch

import pandas as pd
import requests

from app.agents.stock_data_agent import StockDataAgent


class FakeTicker:
    fast_info = {
        "last_price": math.nan,
        "previous_close": math.nan,
        "year_high": math.nan,
        "year_low": math.nan,
        "market_cap": math.nan,
        "last_volume": math.nan,
    }
    info = {
        "longName": "Example Limited",
        "trailingPE": math.nan,
        "fiftyTwoWeekHigh": math.nan,
        "fiftyTwoWeekLow": math.nan,
        "marketCap": math.nan,
        "volume": math.nan,
    }

    def history(self, period, interval, timeout):
        return pd.DataFrame()


class StockDataAgentTests(unittest.TestCase):
    def test_safe_call_logs_external_failure_without_traceback(self):
        agent = StockDataAgent()

        with self.assertLogs(
            "app.agents.stock_data_agent",
            level="WARNING",
        ) as captured:
            result = agent._safe_call(
                lambda: (_ for _ in ()).throw(ConnectionError("reset")),
                timeout_seconds=1,
                label="info",
                ticker="TEST",
            )

        self.assertIsNone(result)
        self.assertEqual(
            captured.output,
            [
                "WARNING:app.agents.stock_data_agent:"
                "yfinance info unavailable for TEST (ConnectionError)"
            ],
        )
        self.assertNotIn("Traceback", captured.output[0])

    @patch("app.agents.stock_data_agent.yf.Ticker")
    @patch.object(
        StockDataAgent,
        "_get_download_price_snapshot",
        return_value={"latest_price": None, "previous_close": None},
    )
    def test_stock_price_uses_info_fallbacks(self, mock_snapshot, mock_ticker):
        fake_ticker = FakeTicker()
        fake_ticker.fast_info = {}
        fake_ticker.info = {
            "currentPrice": 185.5,
            "regularMarketPreviousClose": 182.25,
        }
        mock_ticker.return_value = fake_ticker

        result = StockDataAgent().get_stock_data("TEST")

        self.assertEqual(result["current_price"], 185.5)
        self.assertEqual(result["previous_close"], 182.25)
        self.assertEqual(result["price_change"], 3.25)

    @patch("app.agents.stock_data_agent.yf.Ticker")
    @patch.object(
        StockDataAgent,
        "_get_download_price_snapshot",
        return_value={"latest_price": None, "previous_close": None},
    )
    def test_stock_price_uses_regular_market_price_fallback(
        self,
        mock_snapshot,
        mock_ticker,
    ):
        fake_ticker = FakeTicker()
        fake_ticker.fast_info = {}
        fake_ticker.info = {
            "currentPrice": math.nan,
            "regularMarketPrice": 190.75,
            "previousClose": 189.0,
        }
        mock_ticker.return_value = fake_ticker

        result = StockDataAgent().get_stock_data("TEST")

        self.assertEqual(result["current_price"], 190.75)
        self.assertEqual(result["previous_close"], 189.0)

    @patch("app.agents.stock_data_agent.yf.Ticker", return_value=FakeTicker())
    @patch.object(
        StockDataAgent,
        "_get_download_price_snapshot",
        return_value={"latest_price": None, "previous_close": None},
    )
    def test_stock_response_never_contains_non_finite_numbers(
        self,
        mock_snapshot,
        mock_ticker,
    ):
        result = StockDataAgent().get_stock_data("TEST")

        json.dumps(result, allow_nan=False)
        self.assertIsNone(result["current_price"])
        self.assertIsNone(result["fifty_two_week_high"])
        self.assertIsNone(result["pe_ratio"])

    @patch("app.agents.stock_data_agent.yf.download")
    @patch("app.agents.stock_data_agent.yf.Ticker", return_value=FakeTicker())
    @patch.object(StockDataAgent, "_get_chart_history", return_value=[])
    def test_history_uses_download_fallback(
        self,
        mock_chart_history,
        mock_ticker,
        mock_download,
    ):
        mock_download.return_value = pd.DataFrame(
            {
                ("Open", "TEST"): [100.0],
                ("High", "TEST"): [105.0],
                ("Low", "TEST"): [99.0],
                ("Close", "TEST"): [104.0],
                ("Volume", "TEST"): [1000],
            },
            index=pd.to_datetime(["2026-07-25"]),
        )

        result = StockDataAgent().get_stock_history("TEST", "1mo")

        self.assertEqual(result[0]["close"], 104.0)
        self.assertEqual(result[0]["volume"], 1000)
        mock_download.assert_called_once()
        self.assertEqual(mock_download.call_args.kwargs["interval"], "1d")

    @patch.object(
        StockDataAgent,
        "_get_chart_history",
        return_value=[{"date": "2025-07-25", "close": 104.0, "volume": 1000}],
    )
    def test_history_prefers_direct_chart_data(self, mock_chart_history):
        result = StockDataAgent().get_stock_history("TEST", "1mo")

        self.assertEqual(result[0]["date"], "2025-07-25")
        self.assertEqual(result[0]["close"], 104.0)
        self.assertEqual(result[0]["volume"], 1000)
        mock_chart_history.assert_called_once_with("TEST", "1mo")

    def test_known_company_name_is_available_without_info(self):
        self.assertEqual(
            StockDataAgent()._get_known_company_name("RELIANCE.NS"),
            "Reliance Industries Limited",
        )

    @patch("app.agents.stock_data_agent.requests.get")
    def test_chart_request_retries_alternate_yahoo_host(self, mock_get):
        successful_response = Mock()
        successful_response.json.return_value = {
            "chart": {
                "result": [{"timestamp": [1753401600]}],
                "error": None,
            }
        }
        mock_get.side_effect = [
            requests.ConnectionError("reset"),
            successful_response,
        ]

        result = StockDataAgent()._get_chart_result("TEST", "5d")

        self.assertEqual(result["timestamp"], [1753401600])
        self.assertEqual(mock_get.call_count, 2)
        self.assertIn("query2.finance.yahoo.com", mock_get.call_args.args[0])

    @patch("app.agents.stock_data_agent.requests.get")
    def test_chart_request_uses_period_specific_interval(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "chart": {"result": [{"timestamp": []}], "error": None}
        }
        mock_get.return_value = response

        StockDataAgent()._get_chart_result("TCS.NS", "1d")

        self.assertEqual(mock_get.call_args.kwargs["params"]["interval"], "5m")

    @patch.object(StockDataAgent, "_get_chart_result")
    def test_intraday_history_preserves_distinct_timestamps(self, mock_chart):
        mock_chart.return_value = {
            "timestamp": [1753401600, 1753401900],
            "indicators": {
                "quote": [
                    {
                        "open": [100.0, 101.0],
                        "high": [101.0, 102.0],
                        "low": [99.0, 100.0],
                        "close": [100.5, 101.5],
                        "volume": [1000, 1200],
                    }
                ]
            },
        }

        result = StockDataAgent()._get_chart_history("TCS.NS", "1d")

        self.assertNotEqual(result[0]["date"], result[1]["date"])
        self.assertIn("T", result[0]["date"])

    def test_supported_period_interval_mapping(self):
        agent = StockDataAgent()

        self.assertEqual(agent._history_interval("1d"), "5m")
        self.assertEqual(agent._history_interval("5d"), "1d")
        self.assertEqual(agent._history_interval("1mo"), "1d")
        self.assertEqual(agent._history_interval("6mo"), "1d")


if __name__ == "__main__":
    unittest.main()
