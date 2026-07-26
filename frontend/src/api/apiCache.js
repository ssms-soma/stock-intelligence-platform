const cacheStore = new Map();
const inFlightRequests = new Map();

function devLog(...args) {
  if (import.meta.env.DEV) {
    console.log(...args);
  }
}

export function getCached(key) {
  const entry = cacheStore.get(key);

  if (!entry || Date.now() > entry.expiresAt) {
    if (entry) {
      cacheStore.delete(key);
    }

    devLog("CACHE MISS", key);
    return null;
  }

  devLog("CACHE HIT", key);
  return entry.data;
}

export function setCached(key, data, ttlMs) {
  cacheStore.set(key, {
    data,
    expiresAt: Date.now() + ttlMs,
  });

  return data;
}

export function deleteCached(key) {
  cacheStore.delete(key);
}

export async function getOrFetch(key, fetcher, ttlMs) {
  const cached = getCached(key);

  if (cached !== null && cached !== undefined) {
    return cached;
  }

  if (inFlightRequests.has(key)) {
    devLog("CACHE HIT", `${key}:in-flight`);
    return inFlightRequests.get(key);
  }

  const request = fetcher()
    .then((data) => {
      setCached(key, data, ttlMs);
      return data;
    })
    .finally(() => {
      inFlightRequests.delete(key);
    });

  inFlightRequests.set(key, request);
  return request;
}
