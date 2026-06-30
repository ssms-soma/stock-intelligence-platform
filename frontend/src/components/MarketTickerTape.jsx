import { useEffect, useState } from "react";
import { fetchStockMetrics } from "../api/stockApi";
import {
  formatCurrencyByTicker,
  getMarketInfo,
} from "../utils/marketUtils";

const TICKERS = [
  "AAPL",
  "MSFT",
  "GOOGL",
  "AMZN",
  "TSLA",
  "NVDA",
  "INFY.NS",
  "TCS.NS",
  "RELIANCE.NS",
  "HDFCBANK.NS",
];

function devWarn(...args) {
  if (import.meta.env.DEV) {
    console.warn(...args);
  }
}

function TrendMarker({ direction }) {
  if (direction === "up") {
    return (
      <span
        style={{
          width: 0,
          height: 0,
          borderLeft: "5px solid transparent",
          borderRight: "5px solid transparent",
          borderBottom: "8px solid #22c55e",
        }}
      />
    );
  }

  if (direction === "down") {
    return (
      <span
        style={{
          width: 0,
          height: 0,
          borderLeft: "5px solid transparent",
          borderRight: "5px solid transparent",
          borderTop: "8px solid #ef4444",
        }}
      />
    );
  }

  return (
    <span
      style={{
        width: "8px",
        height: "8px",
        background: "#94a3b8",
      }}
    />
  );
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

async function fetchTickerBatch(tickers) {
  const results = [];

  for (let index = 0; index < tickers.length; index += 2) {
    const batch = tickers.slice(index, index + 2);
    const batchResults = await Promise.allSettled(
      batch.map(async (ticker) => {
        const stock = await fetchStockMetrics(ticker);
        const safeStock = stock && typeof stock === "object" ? stock : {};

        return {
          ...safeStock,
          ticker: safeStock.ticker || ticker,
        };
      })
    );

    results.push(...batchResults);
  }

  return results;
}

function MarketTickerTape({ onTickerSelect }) {
  const [stocks, setStocks] = useState([]);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    async function fetchTickerData() {
      try {
        const results = await fetchTickerBatch(TICKERS);

        const loadedStocks = results
          .filter((result) => result.status === "fulfilled")
          .map((result) => result.value);

        results
          .filter((result) => result.status === "rejected")
          .forEach((result) => {
            devWarn("failed API name:", "ticker tape stock", result.reason);
          });

        setStocks(loadedStocks);
        setFailed(loadedStocks.length === 0);
      } catch (error) {
        devWarn("Market ticker tape fetch error:", error);
        setFailed(true);
      }
    }

    fetchTickerData();
  }, []);

  const tickerItems =
    stocks.length > 0 ? stocks : TICKERS.map((ticker) => ({ ticker }));
  const scrollingItems = [...tickerItems, ...tickerItems];

  return (
    <section
      style={{
        overflow: "hidden",
        borderBottom: "1px solid #1e293b",
        background: "#0f172a",
        color: "#ffffff",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          minHeight: "54px",
          whiteSpace: "nowrap",
        }}
      >
        <div className="market-ticker-track">
          {scrollingItems.map((stock, index) => {
            const trend = stock.trend ?? getStockTrend(stock);
            const direction = trend?.direction ?? "flat";
            const isPositive = direction === "up";
            const isNegative = direction === "down";
            const marketInfo = getMarketInfo(stock.ticker);

            return (
              <button
                type="button"
                key={`${stock.ticker}-${index}`}
                onClick={() => onTickerSelect?.(stock.ticker)}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "0.55rem",
                  minHeight: "54px",
                  padding: "0 1.4rem",
                  borderTop: "none",
                  borderRight: "1px solid #334155",
                  borderBottom: "none",
                  borderLeft: "none",
                  background: "transparent",
                  color: "inherit",
                  cursor: "pointer",
                  fontSize: "0.88rem",
                }}
              >
                <span>{marketInfo.flag}</span>
                <strong style={{ color: "#e2e8f0" }}>{stock.ticker}</strong>
                <span style={{ color: "#e5e7eb" }}>
                  {formatCurrencyByTicker(stock.current_price, stock.ticker)}
                </span>
                <span
                  style={{
                    padding: "0.12rem 0.45rem",
                    border: "1px solid #475569",
                    color: "#cbd5e1",
                    fontSize: "0.72rem",
                    fontWeight: 700,
                  }}
                >
                  {marketInfo.market || "Global"}
                </span>
                {trend?.change !== null &&
                  trend?.change !== undefined && (
                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "0.35rem",
                        color: isPositive
                          ? "#22c55e"
                          : isNegative
                            ? "#ef4444"
                            : "#94a3b8",
                        fontWeight: 700,
                      }}
                    >
                      <TrendMarker direction={direction} />
                      {isPositive ? "+" : ""}
                      {trend.change} ({isPositive ? "+" : ""}
                      {trend.changePercent}%)
                    </span>
                  )}
                {(trend?.change === null ||
                  trend?.change === undefined) && (
                  <span style={{ color: "#94a3b8", fontWeight: 700 }}>
                    {"\u2014"}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {failed && (
        <p
          style={{
            padding: "0 1rem 0.85rem",
            color: "#cbd5e1",
            fontSize: "0.8rem",
          }}
        >
          Market ticker data is temporarily unavailable.
        </p>
      )}
    </section>
  );
}

export default MarketTickerTape;
