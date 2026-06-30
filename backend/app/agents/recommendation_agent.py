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
    }

    SECTOR_MAP = {
        "technology": ["AAPL", "MSFT", "GOOGL", "NVDA"],
        "ecommerce": ["AMZN", "SHOP", "WMT"],
        "indian_it": ["INFY.NS", "TCS.NS", "WIPRO.NS", "TECHM.NS", "HCLTECH.NS"],
        "semiconductors": ["NVDA", "AMD", "INTC", "TSM", "AVGO"],
    }

    def recommend_related_companies(self, ticker: str):
        normalized_ticker = self._normalize_ticker(ticker)

        return {
            "ticker": normalized_ticker,
            "recommendation_type": "related_companies",
            "recommendations": self.RELATED_COMPANY_MAP.get(normalized_ticker, []),
            "method": "rule_based_mapping",
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

    def _normalize_ticker(self, ticker: str):
        return ticker.upper() if ticker else ticker
