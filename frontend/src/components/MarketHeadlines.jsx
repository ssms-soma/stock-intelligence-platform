import { useEffect, useState } from "react";
import SentimentBadge from "./SentimentBadge";

const HEADLINES_URL = "/api/news/stock%20market?page_size=5";

function MarketHeadlines() {
  const [headlines, setHeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    async function fetchHeadlines() {
      try {
        const response = await fetch(HEADLINES_URL);

        if (!response.ok) {
          throw new Error("Failed to fetch market headlines");
        }

        const data = await response.json();
        setHeadlines(Array.isArray(data) ? data : []);
      } catch (error) {
        console.warn("Market headlines fetch error:", error);
        setFailed(true);
      } finally {
        setLoading(false);
      }
    }

    fetchHeadlines();
  }, []);

  return (
    <section
      style={{
        margin: "2rem auto 0",
        maxWidth: "980px",
        textAlign: "left",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "end",
          justifyContent: "space-between",
          gap: "1rem",
          marginBottom: "1rem",
        }}
      >
        <div>
          <p
            style={{
              marginBottom: "0.35rem",
              color: "#64748b",
              fontSize: "0.78rem",
              fontWeight: 700,
              textTransform: "uppercase",
              letterSpacing: "0",
            }}
          >
            Market pulse
          </p>
          <h2 style={{ margin: 0, color: "#0f172a" }}>
            Latest Market Headlines
          </h2>
        </div>
      </div>

      {loading && <p>Loading market headlines...</p>}

      {!loading && failed && (
        <p style={{ color: "#64748b" }}>
          Latest market headlines are temporarily unavailable.
        </p>
      )}

      {!loading && !failed && headlines.length === 0 && (
        <p style={{ color: "#64748b" }}>No market headlines found.</p>
      )}

      {!loading && !failed && headlines.length > 0 && (
        <div
          style={{
            display: "grid",
            gap: "0.85rem",
          }}
        >
          {headlines.map((article) => (
            <article
              key={article.url}
              style={{
                padding: "1rem",
                border: "1px solid #dbe3ef",
                borderLeft: "4px solid #2563eb",
                background: "#ffffff",
                boxShadow: "0 1px 2px rgba(15, 23, 42, 0.05)",
              }}
            >
              <a
                href={article.url}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: "block",
                  marginBottom: "0.6rem",
                  color: "#111827",
                  fontSize: "1rem",
                  fontWeight: 700,
                  textDecoration: "none",
                }}
              >
                {article.title}
              </a>

              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "0.75rem",
                  color: "#475569",
                  fontSize: "0.86rem",
                }}
              >
                <span>
                  <strong>Source:</strong> {article.source ?? "N/A"}
                </span>
                <span>
                  <strong>Sentiment:</strong>{" "}
                  <SentimentBadge sentiment={article.sentiment} />
                </span>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default MarketHeadlines;
