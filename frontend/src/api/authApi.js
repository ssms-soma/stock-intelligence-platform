const API_BASE_URL = "/api";

export class AuthApiError extends Error {
  constructor(message, status = null) {
    super(message);
    this.name = "AuthApiError";
    this.status = status;
  }
}

function getValidationMessage(detail) {
  if (!Array.isArray(detail)) {
    return null;
  }

  const firstMessage = detail.find(
    (item) => typeof item?.msg === "string" && item.msg.trim()
  )?.msg;

  return firstMessage?.replace(/^Value error,\s*/i, "") || null;
}

async function parseResponse(response, fallbackMessage) {
  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const detailMessage =
      typeof data?.detail === "string"
        ? data.detail.trim()
        : getValidationMessage(data?.detail);
    throw new AuthApiError(detailMessage || fallbackMessage, response.status);
  }

  return data;
}

export async function registerUser({ email, password, displayName }) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email.trim(),
      password,
      display_name: displayName?.trim() || null,
    }),
  });

  return parseResponse(response, "Could not create your account.");
}

export async function loginUser({ email, password }) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email.trim(),
      password,
    }),
  });

  return parseResponse(response, "Could not sign in.");
}

export async function fetchCurrentUser(token, { signal } = {}) {
  const response = await fetch(`${API_BASE_URL}/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    signal,
  });

  return parseResponse(response, "Could not restore your session.");
}
