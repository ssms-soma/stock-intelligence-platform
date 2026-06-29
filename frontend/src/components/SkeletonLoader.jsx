function SkeletonLine({ width = "100%", height = "0.85rem" }) {
  return (
    <span
      className="skeleton-shimmer skeleton-line"
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}

export function SkeletonCard() {
  return (
    <section className="skeleton-card" aria-label="Loading stock overview">
      <div>
        <SkeletonLine width="34%" height="0.8rem" />
        <SkeletonLine width="56%" height="1.7rem" />
      </div>
      <SkeletonLine width="28%" height="2.4rem" />
      <SkeletonMetricGrid />
    </section>
  );
}

export function SkeletonMetricGrid({ count = 6 }) {
  return (
    <div className="skeleton-metric-grid">
      {Array.from({ length: count }).map((_, index) => (
        <div className="skeleton-metric" key={index}>
          <SkeletonLine width="52%" height="0.65rem" />
          <SkeletonLine width="72%" height="1.2rem" />
        </div>
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return (
    <section className="skeleton-card" aria-label="Loading price chart">
      <div className="skeleton-row">
        <SkeletonLine width="28%" height="1.3rem" />
        <SkeletonLine width="130px" height="1.8rem" />
      </div>
      <div className="skeleton-chart">
        <SkeletonLine width="92%" height="1px" />
        <SkeletonLine width="84%" height="1px" />
        <SkeletonLine width="88%" height="1px" />
      </div>
    </section>
  );
}

export function SkeletonNewsList({ count = 3 }) {
  return (
    <section className="skeleton-news-list" aria-label="Loading news">
      <SkeletonLine width="160px" height="1.45rem" />
      {Array.from({ length: count }).map((_, index) => (
        <article className="skeleton-news-card" key={index}>
          <SkeletonLine width="76%" height="1.15rem" />
          <SkeletonLine width="38%" height="0.8rem" />
          <SkeletonLine width="100%" height="0.8rem" />
          <SkeletonLine width="88%" height="0.8rem" />
        </article>
      ))}
    </section>
  );
}

export function SkeletonResearchSummary() {
  return (
    <section className="research-summary-card" aria-label="Loading research">
      <div className="skeleton-row">
        <div style={{ flex: 1 }}>
          <SkeletonLine width="180px" height="0.8rem" />
          <SkeletonLine width="44%" height="1.6rem" />
        </div>
        <SkeletonLine width="170px" height="1.8rem" />
      </div>
      <div className="research-insight-strip">
        {Array.from({ length: 6 }).map((_, index) => (
          <div className="research-insight-item" key={index}>
            <SkeletonLine width="56%" height="0.65rem" />
            <SkeletonLine width="74%" height="1rem" />
          </div>
        ))}
      </div>
    </section>
  );
}
