from textblob import TextBlob


class SentimentAgent:
    """
    Handles text sentiment analysis.
    """

    def analyze_sentiment(self, text: str):
        polarity = TextBlob(text).sentiment.polarity

        if polarity > 0.1:
            sentiment = "positive"
        elif polarity < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "polarity": polarity,
        }
