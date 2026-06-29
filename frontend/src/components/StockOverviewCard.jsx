function renderValue(value, fallback = "N/A") {
  if (value === null || value === undefined || value === "") return fallback;
  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return value;
  }
  return fallback;
}

function formatNumber(value, decimals = 2) {
  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return renderValue(value);
  }

  return numberValue.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function formatCompactNumber(value) {
  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return renderValue(value);
  }

  const absValue = Math.abs(numberValue);

  if (absValue >= 1_000_000_000_000) {
    return `${formatNumber(numberValue / 1_000_000_000_000, 2)}T`;
  }

  if (absValue >= 1_000_000_000) {
    return `${formatNumber(numberValue / 1_000_000_000, 1)}B`;
  }

  if (absValue >= 1_000_000) {
    return `${formatNumber(numberValue / 1_000_000, 1)}M`;
  }

  if (absValue >= 1_000) {
    return `${formatNumber(numberValue / 1_000, 1)}K`;
  }

  return formatNumber(numberValue, 0);
}

function formatPrice(value) {
  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return renderValue(value);
  }

  return formatNumber(numberValue, 2);
}

function MetricItem({ label, value }) {
  return (
    <div className="stock-metric-tile">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function StockOverviewCard({ stockData }) {
  const companyName = renderValue(stockData?.company_name, stockData?.ticker);
  const ticker = renderValue(stockData?.ticker);
  const sector = renderValue(stockData?.sector);

  return (
    <section className="stock-overview-card">
      <div className="stock-overview-header">
        <div>
          <p className="stock-overview-eyebrow">Stock Overview</p>
          <h2>{companyName}</h2>
          <div className="stock-overview-meta">
            <span>{ticker}</span>
            <span>{sector}</span>
          </div>
        </div>

        <div className="stock-price-block">
          <span>Current Price</span>
          <strong>{formatPrice(stockData?.current_price)}</strong>
        </div>
      </div>

      <div className="stock-metric-grid">
        <MetricItem
          label="Market Cap"
          value={formatCompactNumber(stockData?.market_cap)}
        />
        <MetricItem label="P/E Ratio" value={formatNumber(stockData?.pe_ratio)} />
        <MetricItem
          label="52-Week High"
          value={formatPrice(stockData?.fifty_two_week_high)}
        />
        <MetricItem
          label="52-Week Low"
          value={formatPrice(stockData?.fifty_two_week_low)}
        />
        <MetricItem label="Volume" value={formatCompactNumber(stockData?.volume)} />
        <MetricItem label="Sector" value={sector} />
      </div>
    </section>
  );
}

export default StockOverviewCard;
