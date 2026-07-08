from app.agents.recommendation_agent import RecommendationAgent
from app.services.company_service import CompanyService
from app.services.stock_service import StockService


class RecommendationService:
    def __init__(self):
        self.recommendation_agent = RecommendationAgent()
        self.stock_service = StockService()
        self.company_service = CompanyService()

    def get_recommendations(self, ticker: str):
        context = self._build_recommendation_context(ticker)
        result = self.recommendation_agent.recommend_related_companies(
            ticker,
            context=context,
        )
        recommendations = result.get("recommendations", [])

        response = {
            "ticker": result.get("ticker"),
            "recommendations": recommendations,
            "recommendation_details": self._build_recommendation_details(
                recommendations,
                result,
                context,
            ),
            "source": "rule_based",
            "method": result.get("method"),
            "sector": result.get("sector"),
            "industry": result.get("industry"),
            "market": result.get("market"),
            "country": result.get("country"),
            "exchange": result.get("exchange"),
            "signals": result.get("signals", {}),
        }

        if not recommendations:
            response["warning"] = "No recommendations found for this ticker."
        elif context.get("warning"):
            response["warning"] = context["warning"]

        return response

    def _build_recommendation_context(self, ticker: str):
        context = {}
        warnings = []

        try:
            stock_data = self.stock_service.get_stock_data(ticker)
        except Exception:
            stock_data = {}
            warnings.append("Stock context is temporarily unavailable.")

        if isinstance(stock_data, dict):
            context.update(
                {
                    "sector": stock_data.get("sector"),
                    "market": stock_data.get("market"),
                    "country": stock_data.get("country"),
                    "exchange": stock_data.get("exchange"),
                    "currency": stock_data.get("currency"),
                    "price_change_percent": stock_data.get("price_change_percent"),
                }
            )

            if stock_data.get("warning"):
                warnings.append(stock_data["warning"])

        try:
            company_result = self.company_service.get_company_profile(ticker)
        except Exception:
            company_result = {}
            warnings.append("Company context is temporarily unavailable.")

        company_profile = (
            company_result.get("company_profile", {})
            if isinstance(company_result, dict)
            else {}
        )

        if isinstance(company_profile, dict):
            for key in [
                "sector",
                "industry",
                "market",
                "country",
                "exchange",
                "currency",
            ]:
                context[key] = context.get(key) or company_profile.get(key)

        cleaned_context = {
            key: value for key, value in context.items() if value not in (None, "")
        }

        if warnings:
            cleaned_context["warning"] = " ".join(warnings)

        return cleaned_context

    def _build_recommendation_details(self, recommendations, result, context):
        if not recommendations:
            return []

        source_ticker = result.get("ticker")
        source_market = result.get("market") or context.get("market")
        source_country = result.get("country") or context.get("country")
        source_exchange = result.get("exchange") or context.get("exchange")
        source_currency = context.get("currency")
        source_sector = result.get("sector") or context.get("sector")
        source_industry = result.get("industry") or context.get("industry")
        static_set = set(
            self.recommendation_agent.RELATED_COMPANY_MAP.get(source_ticker, [])
        )

        return [
            self._build_recommendation_detail(
                recommendation,
                static_set,
                source_market,
                source_country,
                source_exchange,
                source_currency,
                source_sector,
                source_industry,
            )
            for recommendation in recommendations
        ]

    def _build_recommendation_detail(
        self,
        ticker,
        static_set,
        source_market,
        source_country,
        source_exchange,
        source_currency,
        source_sector,
        source_industry,
    ):
        basis = []

        if ticker in static_set:
            basis.append("static_mapping")

        if source_sector:
            basis.append("same_sector")

        if source_market:
            basis.append("same_market")

        if source_industry:
            basis.append("same_industry")

        if not basis:
            basis.append("market_fallback")

        return {
            "ticker": ticker,
            "name": self._get_display_name(ticker),
            "market": source_market or self._infer_market(ticker),
            "country": source_country or self._infer_country(ticker),
            "exchange": self._infer_exchange(ticker, source_exchange),
            "currency": source_currency or self._infer_currency(ticker),
            "reason": self._build_reason(source_sector, source_market, basis),
            "confidence": self._get_confidence(basis),
            "basis": basis,
        }

    def _build_reason(self, sector, market, basis):
        if "static_mapping" in basis and sector and market:
            return f"Related {sector} company in the same {market} market."

        if "static_mapping" in basis:
            return "Related company from the curated rule-based mapping."

        if sector and market:
            return f"Related company selected by sector and {market} market."

        if market:
            return f"Related company selected from the {market} market fallback."

        return "Related company selected by rule-based fallback."

    def _get_confidence(self, basis):
        if "static_mapping" in basis and "same_sector" in basis:
            return 0.85

        if "static_mapping" in basis:
            return 0.8

        if "same_sector" in basis and "same_market" in basis:
            return 0.7

        if "same_market" in basis:
            return 0.6

        return 0.5

    def _get_display_name(self, ticker):
        names = {
            "AAPL": "Apple",
            "MSFT": "Microsoft",
            "GOOGL": "Alphabet",
            "AMZN": "Amazon",
            "NVDA": "NVIDIA",
            "AMD": "AMD",
            "INTC": "Intel",
            "TSM": "TSMC",
            "AVGO": "Broadcom",
            "META": "Meta",
            "ORCL": "Oracle",
            "SHOP": "Shopify",
            "WMT": "Walmart",
            "INFY.NS": "Infosys",
            "TCS.NS": "Tata Consultancy Services",
            "WIPRO.NS": "Wipro",
            "TECHM.NS": "Tech Mahindra",
            "HCLTECH.NS": "HCLTech",
            "RELIANCE.NS": "Reliance Industries",
            "RELIANCE.BO": "Reliance Industries",
            "ONGC.NS": "ONGC",
            "IOC.NS": "Indian Oil",
            "BPCL.NS": "BPCL",
            "ADANIENT.NS": "Adani Enterprises",
            "HDFCBANK.NS": "HDFC Bank",
            "ICICIBANK.NS": "ICICI Bank",
            "KOTAKBANK.NS": "Kotak Mahindra Bank",
            "AXISBANK.NS": "Axis Bank",
            "SBIN.NS": "State Bank of India",
        }

        return names.get(ticker, ticker)

    def _infer_market(self, ticker):
        return "India" if ticker.endswith((".NS", ".BO")) else "United States"

    def _infer_country(self, ticker):
        return "India" if ticker.endswith((".NS", ".BO")) else "United States"

    def _infer_exchange(self, ticker, fallback_exchange):
        if ticker.endswith(".NS"):
            return "NSE"

        if ticker.endswith(".BO"):
            return "BSE"

        return fallback_exchange or "US"

    def _infer_currency(self, ticker):
        return "INR" if ticker.endswith((".NS", ".BO")) else "USD"
