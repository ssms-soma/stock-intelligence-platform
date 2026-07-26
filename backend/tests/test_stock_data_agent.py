import json
import math
import unittest
from unittest.mock import patch

import pandas as pd

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

    def history(self, period, timeout):
        return pd.DataFrame()


class StockDataAgentTests(unittest.TestCase):
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
    def test_history_uses_download_fallback(self, mock_ticker, mock_download):
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


if __name__ == "__main__":
    unittest.main()
