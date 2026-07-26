import re

from textblob import TextBlob


class SentimentAgent:
    """
    Handles text sentiment analysis.
    """

    POSITIVE_TERMS = {
        "beat",
        "beats",
        "gain",
        "gains",
        "growth",
        "profit",
        "profits",
        "rally",
        "record",
        "rise",
        "rises",
        "strong",
        "surge",
        "upgrade",
        "upgrades",
    }
    NEGATIVE_TERMS = {
        "cut",
        "cuts",
        "decline",
        "declines",
        "downgrade",
        "downgrades",
        "drop",
        "drops",
        "fall",
        "falls",
        "lawsuit",
        "loss",
        "losses",
        "miss",
        "misses",
        "probe",
        "slump",
        "weak",
    }

    def analyze_sentiment(self, text: str):
        safe_text = text if isinstance(text, str) else ""
        polarity = TextBlob(safe_text).sentiment.polarity

        if -0.1 <= polarity <= 0.1:
            polarity = self._financial_polarity(safe_text, polarity)

        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "polarity": round(polarity, 3),
        }

    def _financial_polarity(self, text: str, fallback: float):
        words = set(re.findall(r"[a-z]+", text.lower()))
        positive_hits = len(words & self.POSITIVE_TERMS)
        negative_hits = len(words & self.NEGATIVE_TERMS)
        signal_count = positive_hits + negative_hits

        if signal_count == 0 or positive_hits == negative_hits:
            return fallback

        return (positive_hits - negative_hits) / signal_count * 0.25
