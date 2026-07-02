import { getOrFetch } from "./apiCache";

const API_BASE_URL = "/api";
const COMPANY_PROFILE_TTL_MS = 20 * 60 * 1000;

export async function fetchCompanyProfile(ticker) {
  const normalizedTicker = ticker?.trim().toUpperCase();

  if (!normalizedTicker) {
    return null;
  }

  return getOrFetch(`company:${normalizedTicker}`, async () => {
    const response = await fetch(
      `${API_BASE_URL}/company/${encodeURIComponent(normalizedTicker)}`
    );

    if (!response.ok) {
      throw new Error(`Failed to fetch company profile: ${response.status}`);
    }

    return response.json();
  }, COMPANY_PROFILE_TTL_MS);
}
