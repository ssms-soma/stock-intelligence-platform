import { formatCurrencyByTicker, getMarketInfo } from "../utils/marketUtils";

const EMPTY_MESSAGE = "No major signals detected.";

function renderValue(value, fallback) {
  if (value === null || value === undefined || value === "") return fallback;
  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }
  return null;
}

function formatNumber(value, decimals = 2) {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }

  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return renderValue(value, "N/A");
  }

  return numberValue.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function formatPercent(value) {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }

  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    const stringValue = renderValue(value, "N/A");
    return stringValue === "N/A" || stringValue.includes("%")
      ? stringValue
      : `${stringValue}%`;
  }

  return `${numberValue >= 0 ? "+" : ""}${formatNumber(numberValue, 2)}%`;
}

function formatCurrency(value, ticker) {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }

  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return renderValue(value, "N/A");
  }

  return formatCurrencyByTicker(numberValue, ticker);
}

function formatMarketCap(value, ticker) {
  if (value === null || value === undefined || value === "") {
    return "N/A";
  }

  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return renderValue(value, "N/A");
  }

  const marketInfo = getMarketInfo(ticker);

  if (Math.abs(numberValue) >= 1_000_000_000_000) {
    return `${marketInfo.currencySymbol}${formatNumber(
      numberValue / 1_000_000_000_000,
      2
    )}T`;
  }

  if (Math.abs(numberValue) >= 1_000_000_000) {
    return `${marketInfo.currencySymbol}${formatNumber(
      numberValue / 1_000_000_000,
      2
    )}B`;
  }

  if (Math.abs(numberValue) >= 1_000_000) {
    return `${marketInfo.currencySymbol}${formatNumber(
      numberValue / 1_000_000,
      2
    )}M`;
  }

  return formatCurrency(numberValue, ticker);
}

function getToneClass(value) {
  const numberValue = Number(value);

  if (Number.isFinite(numberValue) && numberValue !== 0) {
    return numberValue > 0 ? "tone-positive" : "tone-negative";
  }

  const normalized = String(value || "").toLowerCase();

  if (
    normalized.includes("bullish") ||
    normalized.includes("positive") ||
    normalized.includes("uptrend") ||
    normalized.includes("up") ||
    normalized.includes("strong")
  ) {
    return "tone-positive";
  }

  if (
    normalized.includes("bearish") ||
    normalized.includes("negative") ||
    normalized.includes("downtrend") ||
    normalized.includes("down") ||
    normalized.includes("weak")
  ) {
    return "tone-negative";
  }

  if (
    normalized.includes("risk") ||
    normalized.includes("watch") ||
    normalized.includes("caution") ||
    normalized.includes("elevated")
  ) {
    return "tone-warning";
  }

  return "tone-neutral";
}

function formatKey(key) {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function isPlainObject(value) {
  return value && typeof value === "object" && !Array.isArray(value);
}

function normalizeObject(value) {
  return isPlainObject(value) ? value : {};
}

function normalizeList(value) {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => renderValue(item, ""))
    .filter((item) => item.trim().length > 0);
}

function pickFirstValue(source, keys, fallback = "N/A") {
  for (const key of keys) {
    const value = renderValue(source?.[key], null);

    if (value) {
      return value;
    }
  }

  return fallback;
}

function formatMetricValue(key, value, ticker) {
  const normalizedKey = key.toLowerCase();

  if (normalizedKey.includes("market_cap")) {
    return formatMarketCap(value, ticker);
  }

  if (normalizedKey.includes("price")) {
    return formatCurrency(value, ticker);
  }

  if (normalizedKey.includes("percent") || normalizedKey.includes("margin")) {
    return formatPercent(value);
  }

  if (
    normalizedKey === "pe_ratio" ||
    normalizedKey.includes("ratio") ||
    normalizedKey.includes("multiple")
  ) {
    return formatNumber(value, 2);
  }

  return renderValue(value, "N/A");
}

function Badge({ children, tone = "neutral" }) {
  return <span className={`research-badge tone-${tone}`}>{children}</span>;
}

function getConfidenceTone(confidence) {
  const normalized = String(confidence || "").toLowerCase();
  const numericConfidence = Number(confidence);

  if (Number.isFinite(numericConfidence)) {
    if (numericConfidence >= 70) return "tone-positive";
    if (numericConfidence >= 45) return "tone-neutral";
    return "tone-warning";
  }

  if (normalized.includes("high") || normalized.includes("strong")) {
    return "tone-positive";
  }

  if (normalized.includes("low") || normalized.includes("weak")) {
    return "tone-warning";
  }

  return "tone-neutral";
}

function InsightItem({ label, value, tone }) {
  return (
    <div className={`research-insight-item ${tone}`}>
      <span>{label}</span>
      <strong>{renderValue(value, "N/A")}</strong>
    </div>
  );
}

function Emphasis({ children, toneClass }) {
  return <span className={`research-emphasis ${toneClass}`}>{children}</span>;
}

function AnalystTakeaway({
  summaryText,
  overallView,
  confidence,
  trend,
  priceChangePercent,
  dominantSentiment,
}) {
  return (
    <section className="research-takeaway">
      <div className="research-section-heading">
        <span>Analyst Takeaway</span>
      </div>
      <p>
        <Emphasis toneClass={getToneClass(overallView)}>
          {renderValue(overallView, "Neutral")}
        </Emphasis>{" "}
        view with{" "}
        <Emphasis toneClass="tone-neutral">
          {renderValue(confidence, "N/A")} confidence
        </Emphasis>
        , a{" "}
        <Emphasis toneClass={getToneClass(trend)}>
          {renderValue(trend, "mixed trend")}
        </Emphasis>
        ,{" "}
        <Emphasis toneClass={getToneClass(priceChangePercent)}>
          {formatPercent(priceChangePercent)}
        </Emphasis>{" "}
        price movement, and{" "}
        <Emphasis toneClass={getToneClass(dominantSentiment)}>
          {renderValue(dominantSentiment, "unclear")} news sentiment
        </Emphasis>
        .
      </p>
      <p className="research-takeaway-copy">
        {renderValue(summaryText, "No analyst summary available.")}
      </p>
    </section>
  );
}

function MetricCard({ label, value, toneClass = "tone-neutral" }) {
  return (
    <div className={`research-metric-card ${toneClass}`}>
      <span>{label}</span>
      <strong>{renderValue(value, "N/A")}</strong>
    </div>
  );
}

function MetricSection({ title, children }) {
  return (
    <section className="research-detail-card">
      <h3>{title}</h3>
      <div className="research-metric-grid">{children}</div>
    </section>
  );
}

function PriceAnalysisSection({ priceAnalysis, ticker }) {
  const fields = [
    {
      label: "Start Price",
      value: formatCurrency(priceAnalysis.start_price, ticker),
      toneClass: "tone-neutral",
    },
    {
      label: "Latest Price",
      value: formatCurrency(priceAnalysis.latest_price, ticker),
      toneClass: "tone-neutral",
    },
    {
      label: "Price Change",
      value: formatCurrency(priceAnalysis.price_change, ticker),
      toneClass: getToneClass(priceAnalysis.price_change),
    },
    {
      label: "Price Change %",
      value: formatPercent(priceAnalysis.price_change_percent),
      toneClass: getToneClass(priceAnalysis.price_change_percent),
    },
    {
      label: "Trend",
      value: renderValue(priceAnalysis.trend, "N/A"),
      toneClass: getToneClass(priceAnalysis.trend),
    },
  ];

  const hasAnyValue = fields.some((field) => field.value !== "N/A");

  if (!hasAnyValue) {
    return (
      <section className="research-detail-card">
        <h3>Price Analysis</h3>
        <p className="research-muted">Price analysis is not available yet.</p>
      </section>
    );
  }

  return (
    <MetricSection title="Price Analysis">
      {fields.map((field) => (
        <MetricCard
          key={field.label}
          label={field.label}
          value={field.value}
          toneClass={field.toneClass}
        />
      ))}
    </MetricSection>
  );
}

function ObjectMetricSection({ title, value, fallback, ticker }) {
  const scalarValue = renderValue(value, null);
  const entries = isPlainObject(value) ? Object.entries(value) : [];

  if (scalarValue) {
    return (
      <section className="research-detail-card">
        <h3>{title}</h3>
        <p className="research-body-copy">{scalarValue}</p>
      </section>
    );
  }

  if (entries.length === 0) {
    return (
      <section className="research-detail-card">
        <h3>{title}</h3>
        <p className="research-muted">{fallback}</p>
      </section>
    );
  }

  return (
    <MetricSection title={title}>
      {entries.map(([key, itemValue]) => {
        const displayValue = formatMetricValue(key, itemValue, ticker);

        return (
          <MetricCard
            key={key}
            label={formatKey(key)}
            value={displayValue}
            toneClass={getToneClass(displayValue)}
          />
        );
      })}
    </MetricSection>
  );
}

function SignalSection({ title, label, items, toneClass }) {
  const normalizedItems = normalizeList(items);

  return (
    <section className={`research-signal-card ${toneClass}`}>
      <h3>
        <span className="research-signal-label">{label}</span>
        {title}
      </h3>
      {normalizedItems.length > 0 ? (
        <ul>
          {normalizedItems.map((item, index) => (
            <li key={`${title}-${index}`}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>{EMPTY_MESSAGE}</p>
      )}
    </section>
  );
}

function ResearchSummary({ ticker, researchData, loading, error }) {
  const summary = researchData?.research_summary || {};
  const priceAnalysis = normalizeObject(summary.price_analysis);
  const newsSentiment = isPlainObject(summary.news_sentiment_analysis)
    ? summary.news_sentiment_analysis
    : summary.news_sentiment_analysis;
  const valuation = isPlainObject(summary.valuation_snapshot)
    ? summary.valuation_snapshot
    : summary.valuation_snapshot;
  const normalizedNewsSentiment = normalizeObject(newsSentiment);
  const normalizedValuation = normalizeObject(valuation);

  if (loading) {
    return (
      <section className="research-summary-card">
        <h2>AI Research Summary</h2>
        <p className="research-muted">Loading AI research summary...</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="research-summary-card">
        <h2>AI Research Summary</h2>
        <p className="research-error">{error}</p>
      </section>
    );
  }

  if (!researchData?.research_summary) {
    return (
      <section className="research-summary-card">
        <h2>AI Research Summary</h2>
        <p className="research-muted">
          Research summary is not available for this stock.
        </p>
      </section>
    );
  }

  const overallView = renderValue(summary.overall_view, "Neutral");
  const confidence = renderValue(summary.confidence, "N/A");
  const trend = renderValue(priceAnalysis.trend, "N/A");
  const priceChangePercent = priceAnalysis.price_change_percent;
  const dominantSentiment = pickFirstValue(
    normalizedNewsSentiment,
    ["dominant_sentiment", "overall_sentiment", "sentiment", "tone"],
    renderValue(newsSentiment, "N/A")
  );
  const valuationLabel = pickFirstValue(
    normalizedValuation,
    ["valuation_comment", "comment", "summary", "label", "status"],
    renderValue(valuation, "N/A")
  );
  const displayTicker = renderValue(summary.ticker, ticker || "N/A");
  const companyName = renderValue(summary.company_name, displayTicker);

  return (
    <section className="research-summary-card">
      <div className="research-summary-header">
        <div>
          <p className="research-eyebrow">AI Research Summary</p>
          <h2>{companyName}</h2>
          <p className="research-muted">
            Ticker: <strong>{displayTicker}</strong>
          </p>
        </div>
        <div className="research-header-badges">
          <Badge tone={getToneClass(overallView).replace("tone-", "")}>
            {overallView}
          </Badge>
          <Badge tone={getConfidenceTone(confidence).replace("tone-", "")}>
            Confidence: {confidence}
          </Badge>
        </div>
      </div>

      <div className="research-insight-strip">
        <InsightItem
          label="Overall View"
          value={overallView}
          tone={getToneClass(overallView)}
        />
        <InsightItem
          label="Confidence"
          value={confidence}
          tone={getConfidenceTone(confidence)}
        />
        <InsightItem
          label="1M Price Change"
          value={formatPercent(priceChangePercent)}
          tone={getToneClass(priceChangePercent)}
        />
        <InsightItem label="Trend" value={trend} tone={getToneClass(trend)} />
        <InsightItem
          label="News Sentiment"
          value={dominantSentiment}
          tone={getToneClass(dominantSentiment)}
        />
        <InsightItem
          label="Valuation"
          value={valuationLabel}
          tone={getToneClass(valuationLabel)}
        />
      </div>

      <AnalystTakeaway
        summaryText={summary.analyst_style_summary}
        overallView={overallView}
        confidence={confidence}
        trend={trend}
        priceChangePercent={priceChangePercent}
        dominantSentiment={dominantSentiment}
      />

      <div className="research-summary-grid">
        <PriceAnalysisSection priceAnalysis={priceAnalysis} ticker={displayTicker} />
        <ObjectMetricSection
          title="News Sentiment Analysis"
          value={newsSentiment}
          fallback="News sentiment analysis is not available yet."
          ticker={displayTicker}
        />
        <ObjectMetricSection
          title="Valuation Snapshot"
          value={valuation}
          fallback="Valuation data is not available yet."
          ticker={displayTicker}
        />
      </div>

      <div className="research-signal-grid">
        <SignalSection
          title="Bullish Signals"
          label="Positive"
          items={summary.bullish_signals}
          toneClass="tone-positive"
        />
        <SignalSection
          title="Bearish Signals"
          label="Negative"
          items={summary.bearish_signals}
          toneClass="tone-negative"
        />
        <SignalSection
          title="Risk Factors"
          label="Risk"
          items={summary.risk_factors}
          toneClass="tone-warning"
        />
        <SignalSection
          title="Things To Watch"
          label="Watchlist"
          items={summary.things_to_watch}
          toneClass="tone-neutral"
        />
      </div>

      {renderValue(summary.disclaimer, null) && (
        <p className="research-disclaimer">
          {renderValue(summary.disclaimer, "")}
        </p>
      )}
    </section>
  );
}

export default ResearchSummary;
