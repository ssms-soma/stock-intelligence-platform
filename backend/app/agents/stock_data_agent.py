import logging
import math
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import datetime, timezone
from urllib.parse import quote

import requests
import yfinance as yf

from app.agents.ticker_resolver_agent import TickerResolverAgent
from app.utils.market_utils import get_market_metadata


logger = logging.getLogger(__name__)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)


class StockDataAgent:
    """
    Handles stock market data retrieval.
    """

    INFO_TIMEOUT_SECONDS = 3
    FAST_INFO_TIMEOUT_SECONDS = 4
    HISTORY_TIMEOUT_SECONDS = 8
    FALLBACK_PRICE_TIMEOUT_SECONDS = 5
    HISTORY_INTERVALS = {
        "1d": "5m",
        "5d": "1d",
        "1mo": "1d",
        "6mo": "1d",
    }

    def get_stock_data(self, ticker: str):
        stock = yf.Ticker(ticker)
        warnings = []

        fast_info = self._safe_call(
            lambda: self._collect_fast_info(stock.fast_info),
            timeout_seconds=self.FAST_INFO_TIMEOUT_SECONDS,
            label="fast_info",
            ticker=ticker,
        )

        if fast_info is None:
            warnings.append("Fast stock data is temporarily unavailable.")
            fast_info = {}

        latest_price = self._get_fast_info_value(
            fast_info,
            "last_price",
            "lastPrice",
            "regularMarketPrice",
        )
        previous_close = self._get_fast_info_value(
            fast_info,
            "previous_close",
            "previousClose",
            "regularMarketPreviousClose",
        )

        if latest_price is None or previous_close is None:
            price_snapshot = self._get_download_price_snapshot(ticker)
            latest_price = latest_price or price_snapshot["latest_price"]
            previous_close = previous_close or price_snapshot["previous_close"]

        latest_price = self._safe_float(latest_price)
        previous_close = self._safe_float(previous_close)

        info = self._safe_call(
            lambda: stock.info,
            timeout_seconds=self.INFO_TIMEOUT_SECONDS,
            label="info",
            ticker=ticker,
        )

        if info is None:
            warnings.append("Extended company details are temporarily unavailable.")
            info = {}

        latest_price = self._first_finite_number(
            latest_price,
            info.get("currentPrice"),
            info.get("regularMarketPrice"),
        )
        previous_close = self._first_finite_number(
            previous_close,
            info.get("previousClose"),
            info.get("regularMarketPreviousClose"),
        )

        market_metadata = get_market_metadata(ticker, info)
        stock_data = {
            "ticker": ticker,
            "company_name": (
                info.get("longName")
                or info.get("shortName")
                or self._get_known_company_name(ticker)
                or "N/A"
            ),
            "current_price": latest_price,
            "previous_close": previous_close,
            "price_change": self._calculate_price_change(
                latest_price,
                previous_close,
            ),
            "price_change_percent": self._calculate_price_change_percent(
                latest_price,
                previous_close,
            ),
            "market_cap": self._first_finite_number(
                self._get_fast_info_value(
                    fast_info,
                    "market_cap",
                    "marketCap",
                ),
                info.get("marketCap"),
            ),
            "pe_ratio": self._safe_float(info.get("trailingPE")),
            "fifty_two_week_high": self._first_finite_number(
                self._get_fast_info_value(
                    fast_info,
                    "year_high",
                    "yearHigh",
                    "fiftyTwoWeekHigh",
                ),
                info.get("fiftyTwoWeekHigh"),
            ),
            "fifty_two_week_low": self._first_finite_number(
                self._get_fast_info_value(
                    fast_info,
                    "year_low",
                    "yearLow",
                    "fiftyTwoWeekLow",
                ),
                info.get("fiftyTwoWeekLow"),
            ),
            "volume": self._first_finite_number(
                self._get_fast_info_value(
                    fast_info,
                    "last_volume",
                    "lastVolume",
                    "regularMarketVolume",
                ),
                info.get("volume"),
            ),
            "sector": info.get("sector") or "N/A",
            "market": market_metadata["market"],
            "country": market_metadata["country"],
            "exchange": market_metadata["exchange"],
            "currency": market_metadata["currency"],
            "currency_symbol": market_metadata["currency_symbol"],
        }

        if warnings:
            stock_data["warning"] = " ".join(warnings)

        return stock_data

    def get_stock_history(self, ticker: str, period: str = "6mo"):
        interval = self._history_interval(period)
        chart_history = self._get_chart_history(ticker, period)

        if chart_history:
            return chart_history

        stock = yf.Ticker(ticker)
        history = self._safe_call(
            lambda: stock.history(
                period=period,
                interval=interval,
                timeout=self.HISTORY_TIMEOUT_SECONDS,
            ),
            timeout_seconds=self.HISTORY_TIMEOUT_SECONDS + 2,
            label=f"history:{period}",
            ticker=ticker,
        )

        if history is None or history.empty:
            history = self._safe_call(
                lambda: yf.download(
                    ticker,
                    period=period,
                    interval=interval,
                    progress=False,
                    threads=False,
                    timeout=self.HISTORY_TIMEOUT_SECONDS,
                ),
                timeout_seconds=self.HISTORY_TIMEOUT_SECONDS + 2,
                label=f"download:history:{period}",
                ticker=ticker,
            )

        if history is None or history.empty:
            return []

        return [
            {
                "date": self._format_history_timestamp(index, interval),
                "open": self._round_price(
                    self._get_row_value(row, "Open", ticker)
                ),
                "high": self._round_price(
                    self._get_row_value(row, "High", ticker)
                ),
                "low": self._round_price(
                    self._get_row_value(row, "Low", ticker)
                ),
                "close": self._round_price(
                    self._get_row_value(row, "Close", ticker)
                ),
                "volume": self._safe_int(
                    self._get_row_value(row, "Volume", ticker)
                ),
            }
            for index, row in history.iterrows()
            if self._round_price(self._get_row_value(row, "Close", ticker))
            is not None
        ]

    def _get_download_price_snapshot(self, ticker: str):
        history = self._safe_call(
            lambda: yf.download(
                ticker,
                period="5d",
                interval="1d",
                progress=False,
                threads=False,
                timeout=self.FALLBACK_PRICE_TIMEOUT_SECONDS,
            ),
            timeout_seconds=self.FALLBACK_PRICE_TIMEOUT_SECONDS + 1,
            label="download:fallback_price",
            ticker=ticker,
        )

        if history is None or history.empty:
            return {
                "latest_price": None,
                "previous_close": None,
            }

        latest_close = self._get_history_value(history, -1, "Close", ticker)
        previous_close = self._get_history_value(history, -2, "Close", ticker)

        if previous_close is None:
            previous_close = latest_close

        return {
            "latest_price": self._round_price(latest_close),
            "previous_close": self._round_price(previous_close),
        }

    def _get_chart_history(self, ticker: str, period: str):
        interval = self._history_interval(period)
        chart = self._get_chart_result(ticker, period)

        if not chart:
            return []

        timestamps = chart.get("timestamp") or []
        quotes = (chart.get("indicators") or {}).get("quote") or []
        quote_data = quotes[0] if quotes else {}
        history = []

        for index, timestamp in enumerate(timestamps):
            close = self._chart_value(quote_data, "close", index)

            if self._round_price(close) is None:
                continue

            history.append(
                {
                    "date": self._format_history_timestamp(
                        datetime.fromtimestamp(timestamp, tz=timezone.utc),
                        interval,
                    ),
                    "open": self._round_price(
                        self._chart_value(quote_data, "open", index)
                    ),
                    "high": self._round_price(
                        self._chart_value(quote_data, "high", index)
                    ),
                    "low": self._round_price(
                        self._chart_value(quote_data, "low", index)
                    ),
                    "close": self._round_price(close),
                    "volume": self._safe_int(
                        self._chart_value(quote_data, "volume", index)
                    ),
                }
            )

        return history

    def _get_chart_result(self, ticker: str, period: str):
        def fetch_chart():
            last_error = None
            encoded_ticker = quote(ticker, safe="")

            for host in (
                "query1.finance.yahoo.com",
                "query2.finance.yahoo.com",
                "query1.finance.yahoo.com",
            ):
                try:
                    response = requests.get(
                        f"https://{host}/v8/finance/chart/{encoded_ticker}",
                        params={
                            "range": period or "6mo",
                            "interval": self._history_interval(period),
                            "events": "div,splits",
                        },
                        headers={"User-Agent": "Mozilla/5.0"},
                        timeout=3,
                    )
                    response.raise_for_status()
                    payload = response.json().get("chart") or {}

                    if payload.get("error"):
                        return None

                    results = payload.get("result") or []
                    return results[0] if results else None
                except (requests.RequestException, ValueError) as error:
                    last_error = error

            if last_error:
                raise last_error

            return None

        return self._safe_call(
            fetch_chart,
            timeout_seconds=self.HISTORY_TIMEOUT_SECONDS + 2,
            label=f"chart:{period}",
            ticker=ticker,
        )

    def _history_interval(self, period: str):
        return self.HISTORY_INTERVALS.get(period or "6mo", "1d")

    def _format_history_timestamp(self, value, interval: str):
        if interval == "1d":
            return value.strftime("%Y-%m-%d")

        if hasattr(value, "to_pydatetime"):
            value = value.to_pydatetime()

        return value.isoformat()

    def _chart_value(self, quote_data, field: str, index: int):
        values = quote_data.get(field) or []
        return values[index] if index < len(values) else None

    def _get_known_company_name(self, ticker: str):
        normalized_ticker = ticker.strip().upper() if ticker else ""

        for company in TickerResolverAgent.COMPANY_CATALOG:
            if company["ticker"] == normalized_ticker:
                return company["name"]

        return None

    def _safe_call(self, callback, timeout_seconds: int, label: str, ticker: str):
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(callback)

        try:
            return future.result(timeout=timeout_seconds)
        except TimeoutError:
            logger.warning(
                "yfinance %s timed out for %s after %ss",
                label,
                ticker,
                timeout_seconds,
            )
        except Exception as error:
            logger.warning(
                "yfinance %s unavailable for %s (%s)",
                label,
                ticker,
                type(error).__name__,
            )
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        return None

    def _get_fast_info_value(self, fast_info, *keys):
        for key in keys:
            value = self._read_fast_info(fast_info, key)

            if value is not None:
                return value

        return None

    def _collect_fast_info(self, fast_info):
        return {
            "last_price": self._read_fast_info(fast_info, "last_price"),
            "lastPrice": self._read_fast_info(fast_info, "lastPrice"),
            "regularMarketPrice": self._read_fast_info(
                fast_info,
                "regularMarketPrice",
            ),
            "previous_close": self._read_fast_info(fast_info, "previous_close"),
            "previousClose": self._read_fast_info(fast_info, "previousClose"),
            "regularMarketPreviousClose": self._read_fast_info(
                fast_info,
                "regularMarketPreviousClose",
            ),
            "market_cap": self._read_fast_info(fast_info, "market_cap"),
            "marketCap": self._read_fast_info(fast_info, "marketCap"),
            "year_high": self._read_fast_info(fast_info, "year_high"),
            "yearHigh": self._read_fast_info(fast_info, "yearHigh"),
            "fiftyTwoWeekHigh": self._read_fast_info(fast_info, "fiftyTwoWeekHigh"),
            "year_low": self._read_fast_info(fast_info, "year_low"),
            "yearLow": self._read_fast_info(fast_info, "yearLow"),
            "fiftyTwoWeekLow": self._read_fast_info(fast_info, "fiftyTwoWeekLow"),
            "last_volume": self._read_fast_info(fast_info, "last_volume"),
            "lastVolume": self._read_fast_info(fast_info, "lastVolume"),
            "regularMarketVolume": self._read_fast_info(
                fast_info,
                "regularMarketVolume",
            ),
        }

    def _read_fast_info(self, fast_info, key):
        try:
            if hasattr(fast_info, "get"):
                value = fast_info.get(key)
            else:
                value = getattr(fast_info, key)
        except Exception:
            return None

        return None if value == "N/A" else value

    def _round_price(self, value):
        try:
            number_value = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(number_value):
            return None

        return round(number_value, 2)

    def _safe_int(self, value):
        try:
            number_value = float(value)
        except (TypeError, ValueError):
            return 0

        if not math.isfinite(number_value):
            return 0

        return int(number_value)

    def _get_history_value(self, history, row_index: int, field: str, ticker: str):
        try:
            row = history.iloc[row_index]
        except IndexError:
            return None

        multi_key = (field, ticker)
        if multi_key in row:
            return row.get(multi_key)

        for key, value in row.items():
            if isinstance(key, tuple) and key[0] == field:
                return value

        if field in row:
            return row.get(field)

        return None

    def _get_row_value(self, row, field: str, ticker: str):
        multi_key = (field, ticker)
        if multi_key in row:
            return row.get(multi_key)

        for key, value in row.items():
            if isinstance(key, tuple) and key[0] == field:
                return value

        if field in row:
            return row.get(field)

        return None

    def _first_finite_number(self, *values):
        for value in values:
            number_value = self._safe_float(value)
            if number_value is not None:
                return number_value
        return None

    def _calculate_price_change(self, latest_price, previous_close):
        latest = self._safe_float(latest_price)
        previous = self._safe_float(previous_close)

        if latest is None or previous is None:
            return None

        return round(latest - previous, 2)

    def _calculate_price_change_percent(self, latest_price, previous_close):
        latest = self._safe_float(latest_price)
        previous = self._safe_float(previous_close)

        if latest is None or previous in (None, 0):
            return None

        return round(((latest - previous) / previous) * 100, 2)

    def _safe_float(self, value):
        try:
            number_value = float(value)
        except (TypeError, ValueError):
            return None

        return number_value if math.isfinite(number_value) else None
