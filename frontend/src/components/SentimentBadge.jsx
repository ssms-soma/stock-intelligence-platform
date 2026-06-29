function formatSentiment(sentiment) {
  if (!sentiment) {
    return "Unknown";
  }

  return sentiment.charAt(0).toUpperCase() + sentiment.slice(1).toLowerCase();
}

function getSentimentClass(sentiment) {
  const normalizedSentiment = sentiment?.toLowerCase();

  if (normalizedSentiment === "positive") {
    return "sentiment-positive";
  }

  if (normalizedSentiment === "negative") {
    return "sentiment-negative";
  }

  if (normalizedSentiment === "neutral") {
    return "sentiment-neutral";
  }

  return "sentiment-unknown";
}

function SentimentBadge({ sentiment }) {
  return (
    <span className={`sentiment-badge ${getSentimentClass(sentiment)}`}>
      {formatSentiment(sentiment)}
    </span>
  );
}

export default SentimentBadge;
