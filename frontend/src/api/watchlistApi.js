const API_BASE_URL = "/api";

export class WatchlistApiError extends Error {
  constructor(message, status = null) {
    super(message);
    this.name = "WatchlistApiError";
    this.status = status;
  }
}

async function parseResponse(response, fallbackMessage) {
  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = typeof data?.detail === "string" ? data.detail.trim() : "";
    throw new WatchlistApiError(detail || fallbackMessage, response.status);
  }

  return data;
}

function authHeaders(token, includeJson = false) {
  return {
    Authorization: `Bearer ${token}`,
    ...(includeJson ? { "Content-Type": "application/json" } : {}),
  };
}

export async function fetchWatchlist(token, { signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/watchlist`, {
    headers: authHeaders(token),
    signal,
  });

  return parseResponse(response, "Could not load your watchlist.");
}

export async function addWatchlistItem(token, ticker) {
  const response = await fetch(`${API_BASE_URL}/watchlist`, {
    method: "POST",
    headers: authHeaders(token, true),
    body: JSON.stringify({ ticker }),
  });

  return parseResponse(response, "Could not add this ticker to your watchlist.");
}

export async function removeWatchlistItem(token, ticker) {
  const response = await fetch(
    `${API_BASE_URL}/watchlist/${encodeURIComponent(ticker)}`,
    {
      method: "DELETE",
      headers: authHeaders(token),
    }
  );

  return parseResponse(response, "Could not remove this ticker from your watchlist.");
}
