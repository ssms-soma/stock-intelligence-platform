import { deleteCached, getOrFetch } from "./apiCache";

const API_BASE_URL = "/api";
const STOCK_METRICS_TTL_MS = 60 * 1000;
const STOCK_HISTORY_TTL_MS = 5 * 60 * 1000;

function devLog(...args) {
  if (import.meta.env.DEV) {
    console.log(...args);
  }
}

export async function fetchStockMetrics(ticker) {
  const normalizedTicker = ticker?.trim().toUpperCase();

  if (!normalizedTicker) {
    return null;
  }

  return getOrFetch(`stock:${normalizedTicker}`, async () => {
    const response = await fetch(`${API_BASE_URL}/stocks/${normalizedTicker}`);

    devLog("ticker:", normalizedTicker);
    devLog("stock API status:", response.status);

    if (!response.ok) {
      throw new Error("Failed to fetch stock metrics");
    }

    return response.json();
  }, STOCK_METRICS_TTL_MS);
}

export async function fetchStockHistory(ticker, period = "6mo") {
  const normalizedTicker = ticker?.trim().toUpperCase();
  const normalizedPeriod = period || "6mo";

  if (!normalizedTicker) {
    return [];
  }

  const cacheKey = `history:${normalizedTicker}:${normalizedPeriod}`;
  const history = await getOrFetch(
    cacheKey,
    async () => {
      const response = await fetch(
        `${API_BASE_URL}/stocks/${normalizedTicker}/history?period=${normalizedPeriod}`
      );

      devLog("ticker:", normalizedTicker);
      devLog("history API status:", response.status);

      if (!response.ok) {
        throw new Error("Failed to fetch stock history");
      }

      return response.json();
    },
    STOCK_HISTORY_TTL_MS
  );

  if (!Array.isArray(history) || history.length === 0) {
    deleteCached(cacheKey);
  }

  return Array.isArray(history) ? history : [];
}
