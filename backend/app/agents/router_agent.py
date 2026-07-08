class RouterAgent:
    """
    Purpose:
        Route stock intelligence requests to the existing rule-based services
        that can answer them.

    Responsibilities:
        - Normalize supported request intents.
        - Orchestrate stock, company, news, research, and recommendation
          services without using an LLM.
        - Return consistent routing metadata and warnings for downstream
          chat or API consumers.

    Expected inputs:
        - A ticker and an intent string.

    Expected outputs:
        - A dictionary containing the normalized intent, ticker, agents used,
          result payload, source, and warning.

    Future expansion notes:
        - Phase 3 can add chat intent classification before calling this
          rule-based router.
        - Future LLM/RAG layers can consume this structured output instead of
          calling lower-level services directly.
    """

    SUPPORTED_INTENTS = {
        "stock_overview",
        "company_profile",
        "research",
        "recommendations",
        "news",
    }

    INTENT_ALIASES = {
        "stock": "stock_overview",
        "company": "company_profile",
        "recommendation": "recommendations",
    }

    def __init__(
        self,
        stock_service=None,
        company_service=None,
        news_service=None,
        research_service=None,
        recommendation_agent=None,
        recommendation_service=None,
    ):
        self.stock_service = stock_service
        self.company_service = company_service
        self.news_service = news_service
        self.research_service = research_service
        self.recommendation_agent = recommendation_agent
        self.recommendation_service = recommendation_service

    def route(self, ticker: str, intent: str = "research"):
        normalized_ticker = self._normalize_ticker(ticker)
        normalized_intent = self._normalize_intent(intent)

        if not normalized_ticker:
            return self._unsupported_response(
                normalized_ticker,
                normalized_intent,
                "Invalid ticker.",
            )

        if normalized_intent not in self.SUPPORTED_INTENTS:
            return self._unsupported_response(
                normalized_ticker,
                normalized_intent,
                f"Unsupported intent '{intent}'.",
            )

        if normalized_intent == "stock_overview":
            return self._run_stock_overview_query(normalized_ticker)

        if normalized_intent == "research":
            return self._run_research_query(normalized_ticker)

        if normalized_intent == "recommendations":
            return self._run_recommendations_query(normalized_ticker)

        if normalized_intent == "company_profile":
            return self._run_company_profile_query(normalized_ticker)

        if normalized_intent == "news":
            return self._run_news_query(normalized_ticker)

        return self._unsupported_response(
            normalized_ticker,
            normalized_intent,
            f"Unsupported intent '{intent}'.",
        )

    def route_stock_query(self, ticker: str | None = None):
        return {
            "intent": "stock_analysis",
            "agents": [
                "stock_data",
                "news",
                "research",
            ],
            "context": {
                "ticker": ticker,
            },
        }

    def route_company_query(self, company: str | None = None):
        return {
            "intent": "company_research",
            "agents": [
                "company",
                "stock_data",
                "news",
                "research",
            ],
            "context": {
                "company": company,
            },
        }

    def route_market_query(self, topic: str | None = None):
        return {
            "intent": "market_overview",
            "agents": [
                "news",
                "sentiment",
                "research",
            ],
            "context": {
                "topic": topic,
            },
        }

    def route_general_query(self, query: str | None = None):
        return {
            "intent": "general_stock_question",
            "agents": [
                "router",
                "llm",
            ],
            "context": {
                "query": query,
            },
        }

    def _run_stock_overview_query(self, ticker):
        stock_data = self.stock_service.get_stock_data(ticker)

        return self._response(
            intent="stock_overview",
            ticker=ticker,
            agents_used=["StockDataAgent"],
            result=stock_data,
            warning=stock_data.get("warning") if isinstance(stock_data, dict) else None,
        )

    def _run_research_query(self, ticker):
        result = self.research_service.get_research_report(ticker)

        return self._response(
            intent="research",
            ticker=ticker,
            agents_used=[
                "StockDataAgent",
                "NewsAgent",
                "SentimentAgent",
                "ResearchAgent",
            ],
            result=result,
            warning=self._join_warnings(result.get("warnings")),
        )

    def _run_recommendations_query(self, ticker):
        if self.recommendation_service:
            result = self.recommendation_service.get_recommendations(ticker)
        else:
            result = self.recommendation_agent.recommend_related_companies(ticker)

        warning = None
        if not result.get("recommendations"):
            warning = "No recommendations found for this ticker."
        elif result.get("warning"):
            warning = result["warning"]

        return self._response(
            intent="recommendations",
            ticker=ticker,
            agents_used=["RecommendationAgent"],
            result=result,
            warning=warning,
        )

    def _run_company_profile_query(self, ticker):
        result = self.company_service.get_company_profile(ticker)

        return self._response(
            intent="company_profile",
            ticker=ticker,
            agents_used=["CompanyAgent"],
            result=result,
            warning=result.get("warning") if isinstance(result, dict) else None,
        )

    def _run_news_query(self, ticker):
        stock_data = self.stock_service.get_stock_data(ticker)
        query = stock_data.get("company_name") or ticker
        result = self.news_service.get_stock_news(query, page_size=10)

        return self._response(
            intent="news",
            ticker=ticker,
            agents_used=["StockDataAgent", "NewsAgent", "SentimentAgent"],
            result={
                "query": query,
                "news_data": result,
            },
            warning=self.news_service.last_warning,
        )

    def _response(self, intent, ticker, agents_used, result, warning=None):
        response = {
            "intent": intent,
            "ticker": ticker,
            "agents_used": agents_used,
            "result": result,
            "source": "rule_based_router",
            "warning": warning,
        }

        return response

    def _unsupported_response(self, ticker, intent, warning):
        return self._response(
            intent=intent,
            ticker=ticker,
            agents_used=["router"],
            result=None,
            warning=warning,
        )

    def _join_warnings(self, warnings):
        if not warnings:
            return None

        if isinstance(warnings, list):
            return " ".join(str(warning) for warning in warnings if warning)

        return str(warnings)

    def _normalize_ticker(self, ticker):
        return ticker.strip().upper() if ticker else ""

    def _normalize_intent(self, intent):
        normalized_intent = (intent or "research").strip().lower()
        return self.INTENT_ALIASES.get(normalized_intent, normalized_intent)
