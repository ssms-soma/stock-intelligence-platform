class RouterAgent:
    """
    Purpose:
        Build structured routing plans for user requests in the future
        multi-agent research workflow.

    Responsibilities:
        - Classify broad request intent.
        - Select the agent names that should participate in a workflow.
        - Return routing metadata without executing downstream agents.

    Expected inputs:
        - A user query string, ticker, or market topic depending on the route
          method being called.

    Expected outputs:
        - A dictionary containing the inferred intent, selected agents, and the
          original query context.

    Future expansion notes:
        - Replace these static plans with intent classification, confidence
          scores, and policy rules.
        - Add orchestration metadata such as execution order, dependencies,
          and required retrieval sources.
    """

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
