const API_BASE_URL = "/api";

export async function fetchCompanyNews(query, pageSize = 5) {
  const response = await fetch(
    `${API_BASE_URL}/news/${encodeURIComponent(query)}?page_size=${pageSize}`
  );

  console.log("News API response:", response);

  if (!response.ok) {
    throw new Error(`Failed to fetch news: ${response.status}`);
  }

  return response.json();
}
