import SentimentBadge from "./SentimentBadge";

function NewsCard({ article }) {
  return (
    <div
      style={{
        border: "1px solid #ccc",
        padding: "1rem",
        marginBottom: "1rem",
      }}
    >
      <h3>
        <a href={article.url} target="_blank" rel="noreferrer">
          {article.title}
        </a>
      </h3>

      <p>
        <strong>Source:</strong> {article.source ?? "N/A"}
      </p>
      <p>
        <strong>Published:</strong> {article.published_at ?? "N/A"}
      </p>
      <p>
        <strong>Description:</strong> {article.description ?? "N/A"}
      </p>
      <p>
        <strong>Sentiment:</strong>{" "}
        <SentimentBadge sentiment={article.sentiment} />
      </p>
      <p>
        <strong>Polarity:</strong> {article.polarity ?? "N/A"}
      </p>
    </div>
  );
}

export default NewsCard;
