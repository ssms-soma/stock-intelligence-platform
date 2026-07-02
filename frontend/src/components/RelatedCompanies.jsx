import { useEffect, useMemo, useState } from "react";
import { fetchRecommendations } from "../api/recommendationApi";
import { fetchStockMetrics } from "../api/stockApi";
import {
  formatCurrencyByTicker,
  getMarketInfo,
} from "../utils/marketUtils";

function devWarn(...args) {
  if (import.meta.env.DEV) {
    console.warn(...args);
  }
}

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

function getLocalRelatedTickers(ticker) {
  return RELATED_TICKERS[ticker] ?? getFallbackRelatedTickers(ticker);
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

function getStockTrend(stock) {
  const change = Number(stock?.price_change);
  const changePercent = Number(stock?.price_change_percent);

  if (!Number.isFinite(change) || !Number.isFinite(changePercent)) {
    return null;
  }

  return {
    change,
    changePercent,
    direction: change > 0 ? "up" : change < 0 ? "down" : "flat",
  };
}

function RelatedCompanies({ ticker, onTickerSelect }) {
  const [backendRecommendationResult, setBackendRecommendationResult] =
    useState(null);
  const [relatedStocks, setRelatedStocks] = useState([]);

  const relatedTickers = useMemo(() => {
    const normalizedTicker = ticker?.trim().toUpperCase();

    if (!normalizedTicker) {
      return [];
    }

    return backendRecommendationResult?.ticker === normalizedTicker &&
      backendRecommendationResult.recommendations.length > 0
      ? backendRecommendationResult.recommendations
      : getLocalRelatedTickers(normalizedTicker);
  }, [backendRecommendationResult, ticker]);

  useEffect(() => {
    let isCurrent = true;
    const normalizedTicker = ticker?.trim().toUpperCase();

    async function fetchBackendRecommendations() {
      try {
        const recommendations = await fetchRecommendations(normalizedTicker);

        if (isCurrent && recommendations.length > 0) {
          setBackendRecommendationResult({
            ticker: normalizedTicker,
            recommendations,
          });
        }
      } catch (error) {
        devWarn("failed API name:", "recommendations", error);
      }
    }

    if (normalizedTicker) {
      fetchBackendRecommendations();
    }

    return () => {
      isCurrent = false;
    };
  }, [ticker]);

  useEffect(() => {
    let isCurrent = true;

    async function fetchRelatedCompanies() {
      setRelatedStocks([]);

      const results = await Promise.allSettled(
        relatedTickers.map(async (relatedTicker) => {
          const stock = await fetchStockMetrics(relatedTicker);
          const safeStock = stock && typeof stock === "object" ? stock : {};

          return {
            ...safeStock,
            ticker: safeStock.ticker || relatedTicker,
          };
        })
      );

      results
        .filter((result) => result.status === "rejected")
        .forEach((result) => {
          devWarn("failed API name:", "related company stock", result.reason);
        });

      if (isCurrent) {
        setRelatedStocks(
          results
            .filter((result) => result.status === "fulfilled")
            .map((result) => result.value)
        );
      }
    }

    if (relatedTickers.length > 0) {
      fetchRelatedCompanies();
    }

    return () => {
      isCurrent = false;
    };
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
          const trend = stock.trend ?? getStockTrend(stock);
          const direction = trend?.direction ?? "flat";
          const isUp = direction === "up";
          const isDown = direction === "down";
          const trendColor = isUp ? "#15803d" : isDown ? "#b91c1c" : "#64748b";
          const marketInfo = getMarketInfo(stock.ticker, stock);

          return (
            <button
              type="button"
              key={stock.ticker}
              onClick={() => onTickerSelect?.(stock.ticker)}
              className="related-company-card"
            >
              <span className="related-company-symbol">
                {marketInfo.flag} {stock.ticker}
              </span>
              <span
                style={{
                  color: "#64748b",
                  fontSize: "0.75rem",
                  fontWeight: 700,
                }}
              >
                {marketInfo.exchange || marketInfo.market || "Global"}
              </span>
              <span className="related-company-price">
                {formatCurrencyByTicker(
                  stock.current_price,
                  stock.ticker,
                  stock
                )}
              </span>
              {trend ? (
                <span
                  className="related-company-trend"
                  style={{ color: trendColor }}
                >
                  <TrendMarker direction={direction} />
                  {formatTrendText(trend)}
                </span>
              ) : (
                <span className="related-company-trend" style={{ color: "#64748b" }}>
                  {"\u2014"}
                </span>
              )}
            </button>
          );
        })}
      </div>
    </section>
  );
}

export default RelatedCompanies;
