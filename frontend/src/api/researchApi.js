const API_BASE_URL = "/api";

export async function fetchResearchSummary(ticker) {
  const response = await fetch(
    `${API_BASE_URL}/research/${encodeURIComponent(ticker)}`
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch research summary: ${response.status}`);
  }

  return response.json();
}
