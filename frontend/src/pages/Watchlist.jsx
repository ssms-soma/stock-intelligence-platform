import { useCallback, useEffect, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { fetchWatchlist, WatchlistApiError } from "../api/watchlistApi";
import useAuth from "../auth/useAuth";

function Watchlist() {
  const { token, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);

  const retry = useCallback(() => {
    setRequestVersion((version) => version + 1);
  }, []);

  useEffect(() => {
    if (authLoading || !isAuthenticated || !token) return undefined;

    const controller = new AbortController();
    Promise.resolve()
      .then(() => {
        if (controller.signal.aborted) return [];
        setLoading(true);
        setError("");
        return fetchWatchlist(token, { signal: controller.signal });
      })
      .then((data) => {
        if (!controller.signal.aborted) {
          setItems(Array.isArray(data) ? data : []);
        }
      })
      .catch((requestError) => {
        if (controller.signal.aborted) return;
        if (requestError instanceof WatchlistApiError && requestError.status === 401) {
          logout();
          return;
        }
        setError("Unable to load your watchlist. Please try again.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });

    return () => controller.abort();
  }, [authLoading, isAuthenticated, logout, requestVersion, token]);

  if (authLoading) {
    return <main className="watchlist-page"><p>Checking your session...</p></main>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: "/watchlist" }} />;
  }

  return (
    <main className="watchlist-page">
      <section className="watchlist-panel" aria-labelledby="watchlist-title">
        <p className="watchlist-eyebrow">Your saved stocks</p>
        <h1 id="watchlist-title">Watchlist</h1>
        <p className="watchlist-intro">
          Open a ticker to view its latest public market intelligence.
        </p>

        {loading && items.length === 0 && (
          <p className="watchlist-status" aria-live="polite">Loading watchlist...</p>
        )}

        {error && (
          <div className="watchlist-error" role="alert">
            <p>{error}</p>
            <button type="button" onClick={retry}>Retry</button>
          </div>
        )}

        {!loading && !error && items.length === 0 && (
          <div className="watchlist-empty">
            <p>Your watchlist is empty.</p>
            <Link to="/">Find a stock to watch</Link>
          </div>
        )}

        {items.length > 0 && (
          <div className="watchlist-grid">
            {items.map((item) => (
              <Link
                className="watchlist-card"
                key={item.id}
                to={`/stock/${encodeURIComponent(item.ticker)}`}
              >
                <strong>{item.ticker}</strong>
                <span>View stock intelligence</span>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default Watchlist;
