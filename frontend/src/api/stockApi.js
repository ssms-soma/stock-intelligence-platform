const API_BASE_URL = "/api";

export async function fetchStockMetrics(ticker) {
  const response = await fetch(`${API_BASE_URL}/stocks/${ticker}`);

  if (!response.ok) {
    throw new Error("Failed to fetch stock metrics");
  }

  return response.json();
}

export async function fetchStockHistory(ticker, period = "6mo") {
  const response = await fetch(
    `${API_BASE_URL}/stocks/${ticker}/history?period=${period}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch stock history");
  }

  return response.json();
}
