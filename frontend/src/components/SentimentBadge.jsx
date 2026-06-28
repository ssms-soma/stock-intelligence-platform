const sentimentStyles = {
  positive: {
    color: "green",
  },
  negative: {
    color: "red",
  },
  neutral: {
    color: "#555",
  },
};

function formatSentiment(sentiment) {
  if (!sentiment) {
    return "N/A";
  }

  return sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
}

function SentimentBadge({ sentiment }) {
  const normalizedSentiment = sentiment?.toLowerCase();
  const style = sentimentStyles[normalizedSentiment] ?? {};

  return <span style={style}>{formatSentiment(sentiment)}</span>;
}

export default SentimentBadge;
