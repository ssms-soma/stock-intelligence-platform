import time

from app.agents.company_agent import CompanyAgent


COMPANY_PROFILE_TTL_SECONDS = 20 * 60


class CompanyService:
    def __init__(self):
        self.company_agent = CompanyAgent()
        self._company_cache = {}

    def get_company_profile(self, ticker: str):
        normalized_ticker = self._normalize_ticker(ticker)

        if not normalized_ticker:
            return self.company_agent.get_company_profile(normalized_ticker)

        cached = self._get_cached(self._company_cache, normalized_ticker)

        if cached is not None:
            return cached

        company_profile = self.company_agent.get_company_profile(normalized_ticker)
        self._set_cached(
            self._company_cache,
            normalized_ticker,
            company_profile,
            COMPANY_PROFILE_TTL_SECONDS,
        )
        return company_profile

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
