import { useEffect, useState } from "react";

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

const API_BASE_URL = "/api";

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

  if (!startPrice || !latestPrice) {
    return {
      change: null,
      changePercent: null,
      direction: "flat",
    };
  }

  const change = latestPrice - startPrice;
  const changePercent = (change / startPrice) * 100;

  return {
    change: Number(change.toFixed(2)),
    changePercent: Number(changePercent.toFixed(2)),
    direction: change > 0 ? "up" : change < 0 ? "down" : "flat",
  };
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

function MarketTickerTape({ onTickerSelect }) {
  const [stocks, setStocks] = useState([]);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    async function fetchTickerData() {
      try {
        const results = await Promise.allSettled(
          TICKERS.map(async (ticker) => {
            const [stockResponse, historyResponse] = await Promise.all([
              fetch(`${API_BASE_URL}/stocks/${ticker}`),
              fetch(`${API_BASE_URL}/stocks/${ticker}/history?period=5d`),
            ]);

            if (!stockResponse.ok) {
              throw new Error(`Failed to fetch ${ticker}`);
            }

            const stock = await stockResponse.json();
            const history = historyResponse.ok ? await historyResponse.json() : [];

            return {
              ...stock,
              trend: calculateTrend(history),
            };
          })
        );

        const loadedStocks = results
          .filter((result) => result.status === "fulfilled")
          .map((result) => result.value);

        setStocks(loadedStocks);
        setFailed(loadedStocks.length === 0);
      } catch (error) {
        console.warn("Market ticker tape fetch error:", error);
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
            const direction = stock.trend?.direction ?? "flat";
            const isPositive = direction === "up";
            const isNegative = direction === "down";

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
                <strong style={{ color: "#e2e8f0" }}>{stock.ticker}</strong>
                <span style={{ color: "#e5e7eb" }}>
                  {stock.current_price ?? "Loading"}
                </span>
                {stock.trend?.change !== null &&
                  stock.trend?.change !== undefined && (
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
                      {stock.trend.change} ({isPositive ? "+" : ""}
                      {stock.trend.changePercent}%)
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
