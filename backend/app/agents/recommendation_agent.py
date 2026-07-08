class RecommendationAgent:
    """
    Purpose:
        Generate related-company recommendations for future discovery and
        watchlist workflows.

    Responsibilities:
        - Return rule-based related company suggestions.
        - Provide same-sector recommendation placeholders.
        - Reserve a watchlist recommendation interface for future persistence.

    Expected inputs:
        - A ticker string and, for watchlist workflows, a list of user watchlist
          tickers when persistence is available.

    Expected outputs:
        - Dictionaries containing the requested ticker, recommendation category,
          recommended tickers, and method metadata.

    Future expansion notes:
        - Add ranking, user preference signals, sector embeddings, and social
          discovery signals.
        - Connect watchlist recommendations after database and authentication
          phases are introduced.
    """

    RELATED_COMPANY_MAP = {
        "AAPL": ["MSFT", "GOOGL", "AMZN", "NVDA"],
        "MSFT": ["AAPL", "GOOGL", "AMZN", "ORCL"],
        "GOOGL": ["MSFT", "META", "AMZN", "AAPL"],
        "AMZN": ["WMT", "MSFT", "GOOGL", "SHOP"],
        "NVDA": ["AMD", "INTC", "TSM", "AVGO"],
        "INFY.NS": ["TCS.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS"],
        "TCS.NS": ["INFY.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS"],
        "WIPRO.NS": ["INFY.NS", "TCS.NS", "TECHM.NS", "HCLTECH.NS"],
        "RELIANCE.NS": ["ONGC.NS", "IOC.NS", "BPCL.NS", "ADANIENT.NS"],
        "RELIANCE.BO": ["ONGC.NS", "IOC.NS", "BPCL.NS", "ADANIENT.NS"],
        "HDFCBANK.NS": ["ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SBIN.NS"],
    }

    SECTOR_MAP = {
        "technology": ["AAPL", "MSFT", "GOOGL", "NVDA"],
        "ecommerce": ["AMZN", "SHOP", "WMT"],
        "indian_it": ["INFY.NS", "TCS.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS"],
        "semiconductors": ["NVDA", "AMD", "INTC", "TSM", "AVGO"],
        "indian_energy": ["RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS"],
        "indian_financials": ["HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SBIN.NS"],
    }

    MARKET_FALLBACKS = {
        "India": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"],
        "United States": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
    }

    def recommend_related_companies(self, ticker: str, context=None):
        normalized_ticker = self._normalize_ticker(ticker)
        context = context if isinstance(context, dict) else {}
        static_recommendations = self.RELATED_COMPANY_MAP.get(normalized_ticker, [])
        sector = self._infer_sector(normalized_ticker, context)
        market = context.get("market") or self._infer_market(normalized_ticker)
        recommendations = (
            static_recommendations
            or self._get_sector_recommendations(normalized_ticker, sector)
            or self._get_market_recommendations(normalized_ticker, market)
        )
        signals = self._build_context_signals(context)

        return {
            "ticker": normalized_ticker,
            "recommendation_type": "related_companies",
            "recommendations": recommendations,
            "method": "rule_based_context_mapping"
            if context
            else "rule_based_mapping",
            "sector": sector,
            "industry": context.get("industry"),
            "market": market,
            "country": context.get("country"),
            "exchange": context.get("exchange"),
            "signals": signals,
        }

    def recommend_same_sector(self, ticker: str):
        normalized_ticker = self._normalize_ticker(ticker)
        sector = self._find_sector(normalized_ticker)
        recommendations = [
            candidate
            for candidate in self.SECTOR_MAP.get(sector, [])
            if candidate != normalized_ticker
        ]

        return {
            "ticker": normalized_ticker,
            "recommendation_type": "same_sector",
            "sector": sector,
            "recommendations": recommendations,
            "method": "rule_based_sector_mapping",
        }

    def recommend_from_watchlist(self, watchlist=None):
        return {
            "recommendation_type": "watchlist_based",
            "watchlist": watchlist or [],
            "recommendations": [],
            "method": "placeholder",
            "notes": "Future database and authentication phases will enable user-specific watchlist recommendations.",
        }

    def _find_sector(self, ticker: str):
        for sector, tickers in self.SECTOR_MAP.items():
            if ticker in tickers:
                return sector

        return None

    def _infer_sector(self, ticker: str, context):
        sector = (context.get("sector") or "").lower()
        industry = (context.get("industry") or "").lower()

        if "semiconductor" in sector or "semiconductor" in industry:
            return "semiconductors"

        if "technology" in sector or "software" in industry:
            if ticker.endswith(".NS") or ticker.endswith(".BO"):
                return "indian_it"

            return "technology"

        if "energy" in sector or "oil" in industry or "gas" in industry:
            if ticker.endswith(".NS") or ticker.endswith(".BO"):
                return "indian_energy"

        if (
            "financial" in sector
            or "bank" in industry
            or "bank" in sector
        ) and (ticker.endswith(".NS") or ticker.endswith(".BO")):
            return "indian_financials"

        return self._find_sector(ticker)

    def _infer_market(self, ticker: str):
        if ticker.endswith(".NS") or ticker.endswith(".BO"):
            return "India"

        return "United States"

    def _get_sector_recommendations(self, ticker: str, sector):
        return [
            candidate
            for candidate in self.SECTOR_MAP.get(sector, [])
            if candidate != ticker
        ]

    def _get_market_recommendations(self, ticker: str, market):
        return [
            candidate
            for candidate in self.MARKET_FALLBACKS.get(market, [])
            if candidate != ticker
        ]

    def _build_context_signals(self, context):
        signals = {}

        if "sentiment" in context:
            signals["sentiment"] = context.get("sentiment")

        if "price_change_percent" in context:
            signals["price_change_percent"] = context.get("price_change_percent")

        return signals

    def _normalize_ticker(self, ticker: str):
        return ticker.strip().upper() if ticker else ticker
