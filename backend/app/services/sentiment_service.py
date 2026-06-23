from app.agents.sentiment_agent import SentimentAgent


class SentimentService:
    def __init__(self):
        self.sentiment_agent = SentimentAgent()

    def analyze_sentiment(self, text: str):
        return self.sentiment_agent.analyze_sentiment(text)
