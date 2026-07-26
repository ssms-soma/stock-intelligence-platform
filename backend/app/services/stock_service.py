# Stock service layer
import time

from app.agents.stock_data_agent import StockDataAgent


STOCK_METRICS_TTL_SECONDS = 60
STOCK_HISTORY_TTL_SECONDS = 5 * 60


class StockService:
    def __init__(self):
        self.stock_agent = StockDataAgent()
        self._stock_cache = {}
        self._history_cache = {}

    def get_stock_data(self, ticker: str):
        normalized_ticker = self._normalize_ticker(ticker)
        cache_key = normalized_ticker
        cached = self._get_cached(self._stock_cache, cache_key)

        if cached is not None:
            return cached

        stock_data = self.stock_agent.get_stock_data(normalized_ticker)
        self._set_cached(
            self._stock_cache,
            cache_key,
            stock_data,
            STOCK_METRICS_TTL_SECONDS,
        )
        return stock_data

    def get_stock_history(self, ticker: str, period: str = "6mo"):
        normalized_ticker = self._normalize_ticker(ticker)
        normalized_period = period or "6mo"
        cache_key = f"{normalized_ticker}:{normalized_period}"
        cached = self._get_cached(self._history_cache, cache_key)

        if cached is not None:
            return cached

        history_data = self.stock_agent.get_stock_history(
            normalized_ticker,
            normalized_period,
        )
        if history_data:
            self._set_cached(
                self._history_cache,
                cache_key,
                history_data,
                STOCK_HISTORY_TTL_SECONDS,
            )
        return history_data

    def _get_cached(self, cache, key):
        entry = cache.get(key)

        if not entry:
            return None

        if time.time() > entry["expires_at"]:
            cache.pop(key, None)
            return None

        return entry["data"]

    def _set_cached(self, cache, key, data, ttl_seconds):
        cache[key] = {
            "data": data,
            "expires_at": time.time() + ttl_seconds,
        }

    def _normalize_ticker(self, ticker: str):
        return ticker.strip().upper() if ticker else ""
