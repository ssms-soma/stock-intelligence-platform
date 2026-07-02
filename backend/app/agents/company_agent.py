import logging
import math
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import yfinance as yf

from app.utils.market_utils import get_market_metadata, normalize_ticker


logger = logging.getLogger(__name__)


class CompanyAgent:
    """
    Purpose:
        Provide structured company intelligence placeholders for the future
        multi-agent research layer.

    Responsibilities:
        - Represent company profile, business, sector, headquarters, and peer
          context in a consistent JSON shape.
        - Keep company enrichment separate from stock price and news retrieval.
        - Document future API and RAG integration points.

    Expected inputs:
        - A ticker or company name string.

    Expected outputs:
        - Dictionaries containing normalized company fields and metadata about
          placeholder status.

    Future expansion notes:
        - Integrate company fundamentals APIs for profile, sector, industry,
          and headquarters fields.
        - Use RAG over filings, annual reports, earnings transcripts, and
          curated company notes for business descriptions and competitor maps.
        - Add source attribution once external data providers are connected.
    """

    INFO_TIMEOUT_SECONDS = 5

    PROFILE_FIELDS = [
        "name",
        "long_name",
        "short_name",
        "sector",
        "industry",
        "country",
        "city",
        "state",
        "website",
        "exchange",
        "currency",
        "currency_symbol",
        "market",
        "employees",
        "business_summary",
        "short_summary",
        "description",
        "logo_url",
        "quote_type",
        "price_target",
    ]

    def get_company_profile(self, company: str):
        ticker = self._normalize_ticker(company)
        profile = self._empty_profile(ticker)
        warning = None

        if not ticker:
            return {
                "ticker": ticker,
                "company_profile": profile,
                "source": "yfinance",
                "warning": "Invalid ticker.",
            }

        stock = yf.Ticker(ticker)
        info = self._safe_call(
            lambda: stock.info,
            timeout_seconds=self.INFO_TIMEOUT_SECONDS,
            label="info",
            ticker=ticker,
        )

        if not info or not self._has_profile_data(info):
            warning = "Company profile is temporarily unavailable or ticker was not found."
            info = {}

        metadata = get_market_metadata(ticker, info)
        long_name = self._clean_value(info.get("longName"))
        short_name = self._clean_value(info.get("shortName"))
        business_summary = self._clean_value(info.get("longBusinessSummary"))

        return {
            "ticker": ticker,
            "company_profile": {
                "ticker": ticker,
                "name": long_name or short_name,
                "long_name": long_name,
                "short_name": short_name,
                "sector": self._clean_value(info.get("sector")),
                "industry": self._clean_value(info.get("industry")),
                "country": self._clean_value(info.get("country")) or metadata["country"],
                "city": self._clean_value(info.get("city")),
                "state": self._clean_value(info.get("state")),
                "website": self._clean_value(info.get("website")),
                "exchange": metadata["exchange"],
                "currency": metadata["currency"],
                "currency_symbol": metadata["currency_symbol"],
                "market": metadata["market"],
                "employees": self._clean_value(info.get("fullTimeEmployees")),
                "business_summary": business_summary,
                "short_summary": self._summarize_text(business_summary),
                "description": business_summary,
                "logo_url": self._clean_value(info.get("logo_url"))
                or self._clean_value(info.get("logoUrl")),
                "quote_type": self._clean_value(info.get("quoteType")),
                "price_target": self._build_price_target(info, metadata),
            },
            "source": "yfinance",
            "warning": warning,
        }

    def get_company_business(self, company: str):
        return {
            "company": company,
            "business": {
                "summary": None,
                "segments": [],
                "revenue_drivers": [],
            },
            "source": "phase_2_placeholder",
            "notes": "Future RAG integration can summarize filings and annual reports.",
        }

    def get_company_sector(self, company: str):
        return {
            "company": company,
            "sector": None,
            "industry": None,
            "source": "phase_2_placeholder",
            "notes": "Future fundamentals APIs can populate sector and industry fields.",
        }

    def get_company_headquarters(self, company: str):
        return {
            "company": company,
            "headquarters": {
                "city": None,
                "state": None,
                "country": None,
            },
            "source": "phase_2_placeholder",
            "notes": "Future company profile APIs can populate headquarters metadata.",
        }

    def get_company_competitors(self, company: str):
        return {
            "company": company,
            "competitors": [],
            "source": "phase_2_placeholder",
            "notes": "Future API/RAG integration can build peer groups by sector, industry, and business model.",
        }

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
                "yfinance %s failed for %s: %s",
                label,
                ticker,
                error,
                exc_info=True,
            )
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        return None

    def _empty_profile(self, ticker: str):
        profile = {field: None for field in self.PROFILE_FIELDS}
        profile["ticker"] = ticker
        return profile

    def _normalize_ticker(self, ticker: str):
        return normalize_ticker(ticker)

    def _clean_value(self, value):
        if isinstance(value, float) and not math.isfinite(value):
            return None

        if value in ("", "N/A", "None"):
            return None

        return value

    def _clean_number(self, value):
        try:
            number_value = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(number_value):
            return None

        return round(number_value, 2)

    def _has_profile_data(self, info):
        return any(
            self._clean_value(info.get(key))
            for key in [
                "longName",
                "shortName",
                "sector",
                "industry",
                "website",
                "longBusinessSummary",
                "quoteType",
            ]
        )

    def _summarize_text(self, text, max_words: int = 50):
        cleaned_text = self._clean_value(text)

        if not cleaned_text:
            return None

        words = str(cleaned_text).split()

        if len(words) <= max_words:
            return " ".join(words)

        return f"{' '.join(words[:max_words]).rstrip('.,;:')}."

    def _build_price_target(self, info, metadata):
        price_target = {
            "mean": self._clean_number(info.get("targetMeanPrice")),
            "high": self._clean_number(info.get("targetHighPrice")),
            "low": self._clean_number(info.get("targetLowPrice")),
            "median": self._clean_number(info.get("targetMedianPrice")),
            "currency": metadata["currency"],
            "currency_symbol": metadata["currency_symbol"],
            "analyst_count": self._clean_value(info.get("numberOfAnalystOpinions")),
            "recommendation": self._clean_value(info.get("recommendationKey")),
            "recommendation_mean": self._clean_number(info.get("recommendationMean")),
        }

        if not any(
            price_target[key] is not None
            for key in ["mean", "high", "low", "median", "analyst_count", "recommendation"]
        ):
            return None

        return price_target
