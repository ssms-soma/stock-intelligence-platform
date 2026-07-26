import unittest

from app.agents.sentiment_agent import SentimentAgent


class SentimentAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = SentimentAgent()

    def test_financial_growth_language_is_positive(self):
        result = self.agent.analyze_sentiment(
            "Company profits rise as revenue growth beats estimates"
        )

        self.assertEqual(result["sentiment"], "positive")
        self.assertGreater(result["polarity"], 0.1)

    def test_financial_loss_language_is_negative(self):
        result = self.agent.analyze_sentiment(
            "Shares fall after profit miss and weak forecast"
        )

        self.assertEqual(result["sentiment"], "negative")
        self.assertLess(result["polarity"], -0.1)

    def test_factual_language_remains_neutral(self):
        result = self.agent.analyze_sentiment(
            "Company schedules investor meeting for Monday"
        )

        self.assertEqual(result["sentiment"], "neutral")


if __name__ == "__main__":
    unittest.main()
