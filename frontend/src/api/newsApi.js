import { deleteCached, getOrFetch } from "./apiCache";

const API_BASE_URL = "/api";
const NEWS_TTL_MS = 5 * 60 * 1000;

function devLog(...args) {
  if (import.meta.env.DEV) {
    console.log(...args);
  }
}

export async function fetchCompanyNews(query, pageSize = 5) {
  const normalizedQuery = query?.trim();

  if (!normalizedQuery) {
    return [];
  }

  const cacheKey = `news:${normalizedQuery}:${pageSize}`;
  const articles = await getOrFetch(cacheKey, async () => {
    const response = await fetch(
      `${API_BASE_URL}/news/${encodeURIComponent(normalizedQuery)}?page_size=${pageSize}`
    );

    devLog("News API response:", response);

    if (!response.ok) {
      throw new Error(`Failed to fetch news: ${response.status}`);
    }

    return response.json();
  }, NEWS_TTL_MS);

  if (!Array.isArray(articles) || articles.length === 0) {
    deleteCached(cacheKey);
  }

  return Array.isArray(articles) ? articles : [];
}
