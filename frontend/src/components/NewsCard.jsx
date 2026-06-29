import SentimentBadge from "./SentimentBadge";

function renderValue(value, fallback = "N/A") {
  if (value === null || value === undefined || value === "") return fallback;
  if (typeof value === "string" || typeof value === "number") return value;
  return fallback;
}

function formatPublishedDate(value) {
  const parsedDate = new Date(value);

  if (!value || Number.isNaN(parsedDate.getTime())) {
    return "N/A";
  }

  return parsedDate.toLocaleString(undefined, {
    month: "short",
    day: "2-digit",
    year: "numeric",
  });
}

function NewsCard({ article }) {
  const title = renderValue(article?.title, "Untitled article");
  const url = renderValue(article?.url, "");
  const source = renderValue(article?.source);
  const description = renderValue(
    article?.description,
    "No description available."
  );

  return (
    <article className="news-card">
      <div className="news-card-meta">
        <span>{source}</span>
        <span>{formatPublishedDate(article?.published_at)}</span>
        <SentimentBadge sentiment={article?.sentiment} />
      </div>

      <h3>
        {url ? (
          <a href={url} target="_blank" rel="noopener noreferrer">
            {title}
          </a>
        ) : (
          title
        )}
      </h3>

      <p className="news-card-description">{description}</p>

      {article?.polarity !== null && article?.polarity !== undefined && (
        <p className="news-card-polarity">
          Polarity: <strong>{renderValue(article.polarity)}</strong>
        </p>
      )}
    </article>
  );
}

export default NewsCard;
