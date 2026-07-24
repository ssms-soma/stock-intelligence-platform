const API_BASE_URL = "/api";

export async function resolveTicker(query) {
  const params = new URLSearchParams({ query: query?.trim() || "" });
  const response = await fetch(
    `${API_BASE_URL}/search/resolve?${params.toString()}`
  );

  if (!response.ok) {
    throw new Error(`Failed to resolve ticker: ${response.status}`);
  }

  return response.json();
}
