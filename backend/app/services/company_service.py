import time

from app.agents.company_agent import CompanyAgent
from app.services.stock_service import StockService


COMPANY_PROFILE_TTL_SECONDS = 20 * 60


class CompanyService:
    def __init__(self, company_agent=None, stock_service=None):
        self.company_agent = company_agent or CompanyAgent()
        self.stock_service = stock_service or StockService()
        self._company_cache = {}

    def get_company_profile(self, ticker: str):
        normalized_ticker = self._normalize_ticker(ticker)

        if not normalized_ticker:
            return self.company_agent.get_company_profile(normalized_ticker)

        cached = self._get_cached(self._company_cache, normalized_ticker)

        if cached is not None:
            return cached

        company_profile = self.company_agent.get_company_profile(normalized_ticker)
        if not self._has_usable_company_profile(company_profile):
            company_profile = self._enrich_from_stock(
                company_profile,
                normalized_ticker,
            )
        if self._has_usable_company_profile(company_profile):
            self._set_cached(
                self._company_cache,
                normalized_ticker,
                company_profile,
                COMPANY_PROFILE_TTL_SECONDS,
            )
        return company_profile

    def _enrich_from_stock(self, company_response, ticker):
        response = dict(company_response) if isinstance(company_response, dict) else {}
        profile = dict(response.get("company_profile") or {})

        try:
            stock_data = self.stock_service.get_stock_data(ticker)
        except Exception:
            stock_data = {}

        mappings = {
            "name": "company_name",
            "long_name": "company_name",
            "sector": "sector",
            "market": "market",
            "country": "country",
            "exchange": "exchange",
            "currency": "currency",
            "currency_symbol": "currency_symbol",
        }
        for profile_field, stock_field in mappings.items():
            value = stock_data.get(stock_field) if isinstance(stock_data, dict) else None
            if not profile.get(profile_field) and value not in (None, "", "N/A"):
                profile[profile_field] = value

        profile.setdefault("ticker", ticker)
        response["ticker"] = ticker
        response["company_profile"] = profile
        return response

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

    def _has_usable_company_profile(self, company_response):
        if not isinstance(company_response, dict) or company_response.get("warning"):
            return False

        profile = company_response.get("company_profile")
        if not isinstance(profile, dict):
            return False

        company_fields = (
            "name",
            "long_name",
            "short_name",
            "sector",
            "industry",
            "website",
            "business_summary",
            "description",
        )
        return any(profile.get(field) for field in company_fields)
