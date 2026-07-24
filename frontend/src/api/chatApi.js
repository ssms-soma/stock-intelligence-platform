const API_BASE_URL = "/api";

export async function sendChatMessage({
  message,
  ticker,
  mode = "auto",
  documents = [],
  signal,
}) {
  const normalizedMessage = message?.trim() || "";
  const normalizedTicker = ticker?.trim().toUpperCase() || null;

  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: normalizedMessage,
      ticker: normalizedTicker,
      mode,
      documents: Array.isArray(documents) ? documents : [],
    }),
    signal,
  });

  if (!response.ok) {
    throw new Error("AI Research Assistant request failed.");
  }

  return response.json();
}
