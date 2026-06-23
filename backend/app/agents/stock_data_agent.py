import yfinance as yf


class StockDataAgent:
    """
    Handles stock market data retrieval.
    """

    def get_stock_data(self, ticker: str):
        stock = yf.Ticker(ticker)

        info = stock.info

        return {
            "ticker": ticker,
            "company_name": info.get("longName"),
            "current_price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "volume": info.get("volume"),
            "sector": info.get("sector"),
        }

    def get_stock_history(self, ticker: str, period: str = "6mo"):
        history = yf.Ticker(ticker).history(period=period)

        return [
            {
                "date": index.strftime("%Y-%m-%d"),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"]),
            }
            for index, row in history.iterrows()
        ]
