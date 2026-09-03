const ACCESS_TOKEN_KEY = "stock-intelligence.auth.access-token";

export function readAccessToken() {
  try {
    return window.localStorage.getItem(ACCESS_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function storeAccessToken(token) {
  try {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, token);
    return true;
  } catch {
    return false;
  }
}

export function removeAccessToken() {
  try {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  } catch {
    // In-memory auth state is still cleared when browser storage is unavailable.
  }
}
