import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import {
  addWatchlistItem,
  fetchWatchlist,
  removeWatchlistItem,
  WatchlistApiError,
} from "../api/watchlistApi";
import useAuth from "../auth/useAuth";

function WatchlistButton({ ticker }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { token, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const normalizedTicker = ticker?.trim().toUpperCase() || "";
  const [isWatched, setIsWatched] = useState(false);
  const [resolvedTicker, setResolvedTicker] = useState("");
  const [resolvedToken, setResolvedToken] = useState("");
  const [loading, setLoading] = useState(false);
  const [mutating, setMutating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isAuthenticated || !token || !normalizedTicker) {
      return undefined;
    }

    const controller = new AbortController();
    Promise.resolve()
      .then(() => {
        if (controller.signal.aborted) return [];
        setLoading(true);
        setError("");
        return fetchWatchlist(token, { signal: controller.signal });
      })
      .then((items) => {
        if (controller.signal.aborted) return;
        setIsWatched(
          Array.isArray(items) &&
            items.some((item) => item?.ticker === normalizedTicker)
        );
        setResolvedTicker(normalizedTicker);
        setResolvedToken(token);
      })
      .catch((requestError) => {
        if (controller.signal.aborted) return;
        if (requestError instanceof WatchlistApiError && requestError.status === 401) {
          logout();
          return;
        }
        setError("Could not check your watchlist.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [isAuthenticated, logout, normalizedTicker, token]);

  async function handleClick() {
    if (!isAuthenticated || !token) {
      navigate("/login", { state: { from: location.pathname } });
      return;
    }

    setMutating(true);
    setError("");
    const currentlyWatched =
      resolvedToken === token &&
      resolvedTicker === normalizedTicker &&
      isWatched;

    try {
      if (currentlyWatched) {
        await removeWatchlistItem(token, normalizedTicker);
        setIsWatched(false);
      } else {
        await addWatchlistItem(token, normalizedTicker);
        setIsWatched(true);
      }
      setResolvedTicker(normalizedTicker);
      setResolvedToken(token);
    } catch (requestError) {
      if (requestError instanceof WatchlistApiError) {
        if (requestError.status === 401) {
          logout();
          navigate("/login", { state: { from: location.pathname } });
          return;
        }
        if (requestError.status === 409) {
          setIsWatched(true);
          setResolvedTicker(normalizedTicker);
          setResolvedToken(token);
          return;
        }
      }
      setError("Watchlist update failed. Please try again.");
    } finally {
      setMutating(false);
    }
  }

  const effectiveLoading = isAuthenticated && loading;
  const disabled = authLoading || effectiveLoading || mutating || !normalizedTicker;
  const currentlyWatched =
    isAuthenticated &&
    resolvedToken === token &&
    resolvedTicker === normalizedTicker &&
    isWatched;
  const label = mutating
    ? currentlyWatched
      ? "Removing..."
      : "Adding..."
    : effectiveLoading
      ? "Checking..."
      : currentlyWatched
        ? "Watching"
        : "Watch";

  return (
    <div className="watchlist-control">
      <button
        className={`watchlist-button${currentlyWatched ? " is-watching" : ""}`}
        type="button"
        onClick={handleClick}
        disabled={disabled}
        aria-pressed={currentlyWatched}
      >
        {label}
      </button>
      {error && <span className="watchlist-control-error" role="alert">{error}</span>}
    </div>
  );
}

export default WatchlistButton;
