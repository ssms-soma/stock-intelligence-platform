from app.agents.ticker_resolver_agent import TickerResolverAgent


class TickerResolverService:
    def __init__(self):
        self.ticker_resolver_agent = TickerResolverAgent()

    def resolve(self, query: str):
        return self.ticker_resolver_agent.resolve(query)
