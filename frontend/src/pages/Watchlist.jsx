import { useCallback, useEffect, useRef, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { fetchWatchlist, removeWatchlistItem, WatchlistApiError } from "../api/watchlistApi";
import useAuth from "../auth/useAuth";

function Watchlist() {
  const { token, isAuthenticated, isLoading: authLoading, logout } = useAuth();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [requestVersion, setRequestVersion] = useState(0);
  const [query, setQuery] = useState("");
  const [removing, setRemoving] = useState([]);
  const [removeErrors, setRemoveErrors] = useState({});
  const searchInput = useRef(null);
  const removalSession = useRef(null);

  const normalizedQuery = query.trim().toLowerCase();
  const filteredItems = normalizedQuery
    ? items.filter((item) => item.ticker.toLowerCase().includes(normalizedQuery))
    : items;

  useEffect(() => {
    const session = { active: true, pending: new Set() };
    removalSession.current = session;
    return () => { session.active = false; };
  }, [token]);

  async function handleRemove(ticker) {
    const session = removalSession.current;
    if (!session?.active || session.pending.has(ticker)) return;
    if (!window.confirm(`Remove ${ticker} from your watchlist?`)) return;

    session.pending.add(ticker);
    setRemoving((current) => [...current, ticker]);
    setRemoveErrors((current) => ({ ...current, [ticker]: "" }));
    try {
      await removeWatchlistItem(token, ticker);
      if (session.active) {
        setItems((current) => current.filter((item) => item.ticker !== ticker));
      }
    } catch (requestError) {
      if (!session.active) return;
      if (requestError instanceof WatchlistApiError && requestError.status === 401) {
        logout();
        return;
      }
      setRemoveErrors((current) => ({
        ...current, [ticker]: "Could not remove this ticker. Please try Remove again.",
      }));
    } finally {
      session.pending.delete(ticker);
      if (session.active) {
        setRemoving((current) => current.filter((value) => value !== ticker));
      }
    }
  }

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
    <main className="watchlist-page watchlist-list-page">
      <section className="watchlist-panel" aria-labelledby="watchlist-title">
        <p className="watchlist-eyebrow">Your saved stocks</p>
        <h1 id="watchlist-title">Watchlist</h1>
        <p className="watchlist-intro">
          Open a ticker to view its latest public market intelligence.
        </p>

        {!loading && !error && items.length > 0 && (
          <div className="watchlist-toolbar">
            <div className="watchlist-search">
              <label htmlFor="watchlist-search">Search watchlist</label>
              <input id="watchlist-search" ref={searchInput} type="search"
                placeholder="Search by ticker" value={query}
                onChange={(event) => setQuery(event.target.value)} />
            </div>
            {query.length > 0 && <button type="button" className="watchlist-clear"
              onClick={() => {
                setQuery("");
                searchInput.current?.focus();
              }}>Clear search</button>}
          </div>
        )}

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
            <p>Open a stock page and choose Watch to save it here.</p>
            <Link to="/">Find a stock to watch</Link>
          </div>
        )}

        {!loading && !error && items.length > 0 && <div role="status">
          {filteredItems.length === 0 && <p className="watchlist-empty">
            No watchlist items match your search.
          </p>}
        </div>}

        {filteredItems.length > 0 && (
          <div className="watchlist-grid">
            {filteredItems.map((item) => (
              <article className="watchlist-card" key={item.id}>
                <strong>{item.ticker}</strong>
                <div className="watchlist-actions">
                  <Link to={`/stock/${encodeURIComponent(item.ticker)}`}
                    aria-label={`View stock intelligence for ${item.ticker}`}>View stock intelligence</Link>
                  <button type="button" disabled={removing.includes(item.ticker)}
                    aria-label={`Remove ${item.ticker} from your watchlist`}
                    onClick={() => handleRemove(item.ticker)}>
                    {removing.includes(item.ticker) ? "Removing..." : "Remove"}
                  </button>
                </div>
                {removeErrors[item.ticker] && <p className="watchlist-remove-error" role="alert">
                  {removeErrors[item.ticker]}
                </p>}
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default Watchlist;
