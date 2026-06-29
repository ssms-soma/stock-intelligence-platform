import { useEffect, useMemo, useState } from "react";
import { fetchStockHistory, fetchStockMetrics } from "../api/stockApi";

const RELATED_TICKERS = {
  "INFY.NS": ["TCS.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
  "TCS.NS": ["INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
  "RELIANCE.NS": ["ONGC.NS", "IOC.NS", "BPCL.NS", "ADANIENT.NS"],
  "HDFCBANK.NS": ["ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SBIN.NS"],
  AAPL: ["MSFT", "GOOGL", "AMZN", "NVDA"],
  MSFT: ["AAPL", "GOOGL", "AMZN", "NVDA"],
  GOOGL: ["META", "MSFT", "AMZN", "AAPL"],
  AMZN: ["GOOGL", "MSFT", "META", "TSLA"],
  TSLA: ["AAPL", "NVDA", "AMZN", "GOOGL"],
  NVDA: ["AMD", "MSFT", "AAPL", "GOOGL"],
};

function getFallbackRelatedTickers(ticker) {
  if (ticker.endsWith(".NS")) {
    return ["INFY.NS", "TCS.NS", "RELIANCE.NS", "HDFCBANK.NS"].filter(
      (relatedTicker) => relatedTicker !== ticker
    );
  }

  return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"].filter(
    (relatedTicker) => relatedTicker !== ticker
  );
}

function calculateTrend(historyData) {
  if (!Array.isArray(historyData) || historyData.length < 2) {
    return {
      change: null,
      changePercent: null,
      direction: "flat",
    };
  }

  const startPrice = Number(historyData[0]?.close);
  const latestPrice = Number(historyData[historyData.length - 1]?.close);

  if (!Number.isFinite(startPrice) || !Number.isFinite(latestPrice) || startPrice === 0) {
    return {
      change: null,
      changePercent: null,
      direction: "flat",
    };
  }

  const change = latestPrice - startPrice;
  const changePercent = (change / startPrice) * 100;

  return {
    change,
    changePercent,
    direction: change > 0 ? "up" : change < 0 ? "down" : "flat",
  };
}

function formatPrice(value) {
  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return "Loading...";
  }

  return numberValue.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function formatTrendValue(value) {
  const numberValue = Number(value);

  if (!Number.isFinite(numberValue)) {
    return "N/A";
  }

  return `${numberValue >= 0 ? "+" : ""}${numberValue.toFixed(2)}`;
}

function formatTrendText(trend) {
  if (
    !trend ||
    !Number.isFinite(Number(trend.change)) ||
    !Number.isFinite(Number(trend.changePercent))
  ) {
    return "Trend pending";
  }

  return `${formatTrendValue(trend.change)} (${formatTrendValue(
    trend.changePercent
  )}%)`;
}

function TrendMarker({ direction }) {
  if (direction === "up") {
    return <span className="related-trend-triangle related-trend-up" />;
  }

  if (direction === "down") {
    return <span className="related-trend-triangle related-trend-down" />;
  }

  return <span className="related-trend-flat" />;
}

function RelatedCompanies({ ticker, onTickerSelect }) {
  const [relatedStocks, setRelatedStocks] = useState([]);

  const relatedTickers = useMemo(() => {
    const normalizedTicker = ticker?.toUpperCase();

    if (!normalizedTicker) {
      return [];
    }

    return RELATED_TICKERS[normalizedTicker] ?? getFallbackRelatedTickers(normalizedTicker);
  }, [ticker]);

  useEffect(() => {
    async function fetchRelatedCompanies() {
      setRelatedStocks([]);

      const results = await Promise.allSettled(
        relatedTickers.map(async (relatedTicker) => {
          const [stock, history] = await Promise.all([
            fetchStockMetrics(relatedTicker),
            fetchStockHistory(relatedTicker, "5d").catch(() => []),
          ]);

          return {
            ...stock,
            trend: calculateTrend(history),
          };
        })
      );

      setRelatedStocks(
        results
          .filter((result) => result.status === "fulfilled")
          .map((result) => result.value)
      );
    }

    if (relatedTickers.length > 0) {
      fetchRelatedCompanies();
    }
  }, [relatedTickers]);

  if (relatedTickers.length === 0) {
    return null;
  }

  const displayedStocks =
    relatedStocks.length > 0
      ? relatedStocks
      : relatedTickers.map((relatedTicker) => ({ ticker: relatedTicker }));

  return (
    <section
      style={{
        marginTop: "2rem",
        padding: "1rem",
        border: "1px solid #dbe3ef",
        background: "#ffffff",
        textAlign: "left",
      }}
    >
      <h2 style={{ marginBottom: "1rem", color: "#0f172a" }}>
        Related Companies
      </h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
          gap: "0.75rem",
        }}
      >
        {displayedStocks.map((stock) => {
          const direction = stock.trend?.direction ?? "flat";
          const isUp = direction === "up";
          const isDown = direction === "down";
          const trendColor = isUp ? "#15803d" : isDown ? "#b91c1c" : "#64748b";

          return (
            <button
              type="button"
              key={stock.ticker}
              onClick={() => onTickerSelect?.(stock.ticker)}
              className="related-company-card"
            >
              <span className="related-company-symbol">{stock.ticker}</span>
              <span className="related-company-price">
                {formatPrice(stock.current_price)}
              </span>
              <span
                className="related-company-trend"
                style={{ color: trendColor }}
              >
                <TrendMarker direction={direction} />
                {formatTrendText(stock.trend)}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

export default RelatedCompanies;
