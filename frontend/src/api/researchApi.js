import { getOrFetch } from "./apiCache";

const API_BASE_URL = "/api";
const RESEARCH_TTL_MS = 5 * 60 * 1000;

export async function fetchResearchSummary(ticker) {
  const normalizedTicker = ticker?.trim().toUpperCase();

  if (!normalizedTicker) {
    return null;
  }

  return getOrFetch(`research:${normalizedTicker}`, async () => {
    const response = await fetch(
      `${API_BASE_URL}/research/${encodeURIComponent(normalizedTicker)}`
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch research summary: ${response.status}`);
    }

    return response.json();
  }, RESEARCH_TTL_MS);
}
