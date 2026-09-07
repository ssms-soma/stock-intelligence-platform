export class SavedResearchApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "SavedResearchApiError";
    this.status = status;
  }
}

async function request(token, path = "", { body, ...options } = {}) {
  const response = await fetch(`/api/saved-research${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...(body ? { "Content-Type": "application/json" } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new SavedResearchApiError(
      typeof data?.detail === "string" ? data.detail : "Saved research request failed. Please try again.",
      response.status,
    );
  }
  return data;
}

export const fetchSavedResearch = (token, options) => request(token, "", options);
export const fetchSavedResearchDetail = (token, id, options) =>
  request(token, `/${encodeURIComponent(id)}`, options);
export const saveResearch = (token, ticker, content, options) =>
  request(token, "", { ...options, method: "POST", body: { ticker, content } });
export const deleteSavedResearch = (token, id, options) =>
  request(token, `/${encodeURIComponent(id)}`, { ...options, method: "DELETE" });
