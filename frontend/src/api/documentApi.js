const API_BASE_URL = "/api";

export class DocumentApiError extends Error {
  constructor(message, status = null) {
    super(message);
    this.name = "DocumentApiError";
    this.status = status;
  }
}

async function parseResponse(response, fallbackMessage) {
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const backendWarning = data?.detail?.warning;
    const safeMessage =
      typeof backendWarning === "string" && backendWarning.trim()
        ? backendWarning.trim()
        : fallbackMessage;
    throw new DocumentApiError(safeMessage, response.status);
  }

  return data;
}

export async function uploadDocument({ file, signal }) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    body: formData,
    signal,
  });

  return parseResponse(response, "Could not upload this document.");
}

export async function askUploadedDocument({
  documentId,
  question,
  topK = 5,
  signal,
}) {
  const response = await fetch(
    `${API_BASE_URL}/documents/${encodeURIComponent(documentId)}/ask`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: question?.trim() || "",
        top_k: topK,
      }),
      signal,
    }
  );

  return parseResponse(
    response,
    "The AI Research Assistant is temporarily unavailable."
  );
}
