import { getOrFetch } from "./apiCache";

const API_BASE_URL = "/api";
const RECOMMENDATIONS_TTL_MS = 5 * 60 * 1000;

export async function fetchRecommendations(ticker) {
  const normalizedTicker = ticker?.trim().toUpperCase();

  if (!normalizedTicker) {
    return [];
  }

  return getOrFetch(`recommendations:${normalizedTicker}`, async () => {
    const response = await fetch(
      `${API_BASE_URL}/recommendations/${encodeURIComponent(normalizedTicker)}`
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch recommendations: ${response.status}`);
    }

    const data = await response.json();

    return Array.isArray(data?.recommendations) ? data.recommendations : [];
  }, RECOMMENDATIONS_TTL_MS);
}
