import { useEffect, useRef, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { deleteSavedResearch, fetchSavedResearch } from "../api/savedResearchApi";
import useAuth from "../auth/useAuth";

function formatSavedDate(value) {
  const date = new Date(value);
  if (!value || Number.isNaN(date.getTime())) return "Date unavailable";
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function SavedResearch() {
  const { token, isAuthenticated, isLoading, logout } = useAuth();
  if (isLoading) return <main className="watchlist-page">Checking your session...</main>;
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: "/saved-research" }} />;
  return <SavedResearchList key={token} token={token} logout={logout} />;
}

function SavedResearchList({ token, logout }) {
  const [items, setItems] = useState([]);
  const [query, setQuery] = useState("");
  const searchInput = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);
  const [deleting, setDeleting] = useState([]);
  const [deleteErrors, setDeleteErrors] = useState({});
  const deleteControllers = useRef(new Map());

  const normalizedQuery = query.trim().toLowerCase();
  const filteredItems = normalizedQuery
    ? items.filter((item) =>
        item.ticker.toLowerCase().includes(normalizedQuery) ||
        item.title.toLowerCase().includes(normalizedQuery)
      )
    : items;

  useEffect(() => {
    const controllers = deleteControllers.current;
    return () => controllers.forEach((controller) => controller.abort());
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    fetchSavedResearch(token, { signal: controller.signal })
      .then((data) => {
        if (!controller.signal.aborted) setItems(data);
      })
      .catch((requestError) => {
        if (controller.signal.aborted) return;
        if (requestError.status === 401) return logout();
        setError("Unable to load saved research. Please try again.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [logout, retry, token]);

  async function handleDelete(id, title) {
    if (deleteControllers.current.has(id)) return;
    if (!window.confirm(`Delete saved research “${title}”? This cannot be undone.`)) return;
    const controller = new AbortController();
    deleteControllers.current.set(id, controller);
    setDeleting((current) => [...current, id]);
    setDeleteErrors((current) => ({ ...current, [id]: "" }));
    try {
      await deleteSavedResearch(token, id, { signal: controller.signal });
      if (!controller.signal.aborted) setItems((current) => current.filter((item) => item.id !== id));
    } catch (requestError) {
      if (controller.signal.aborted) return;
      if (requestError.status === 401) return logout();
      if (requestError.status === 404) {
        setItems((current) => current.filter((item) => item.id !== id));
      } else {
        setDeleteErrors((current) => ({ ...current, [id]: "Could not delete. Please try again." }));
      }
    } finally {
      deleteControllers.current.delete(id);
      if (!controller.signal.aborted) setDeleting((current) => current.filter((value) => value !== id));
    }
  }

  return (
    <main className="watchlist-page saved-research-page">
      <section className="watchlist-panel" aria-labelledby="saved-research-title">
        <p className="watchlist-eyebrow">Your research snapshots</p>
        <h1 id="saved-research-title">Saved Research</h1>
        <p className="watchlist-intro">Open research as it was when you saved it.</p>
        {!loading && !error && items.length > 0 && <div className="saved-research-toolbar">
          <div className="saved-research-search">
            <label htmlFor="saved-research-search">Search saved research</label>
            <input id="saved-research-search" ref={searchInput} type="search"
              placeholder="Search by ticker or title" value={query}
              onChange={(event) => setQuery(event.target.value)} />
          </div>
          {query.length > 0 && <button type="button" className="saved-research-clear"
            onClick={() => {
              setQuery("");
              searchInput.current?.focus();
            }}>Clear search</button>}
        </div>}
        {loading && <p aria-live="polite">Loading saved research...</p>}
        {error && <div className="watchlist-error" role="alert">
          <p>{error}</p>
          <button type="button" onClick={() => {
            setLoading(true); setError(""); setRetry((value) => value + 1);
          }}>Retry</button>
        </div>}
        {!loading && !error && items.length === 0 && <div className="watchlist-empty">
          <p>You have no saved research yet.</p>
          <p>Open a stock page and choose Save Research in the AI Research Summary.</p>
          <Link to="/">Find a stock to research</Link>
        </div>}
        {!loading && !error && items.length > 0 && <div role="status">
          {filteredItems.length === 0 && <p className="watchlist-empty saved-research-filtered-empty">
            No saved research matches your search.
          </p>}
        </div>}
        <div className="watchlist-grid">
          {filteredItems.map((item) => <article className="watchlist-card" key={item.id}>
            <strong>{item.ticker}</strong>
            <h2 className="saved-research-title">{item.title}</h2>
            <time dateTime={item.created_at}>Saved {formatSavedDate(item.created_at)}</time>
            <div className="saved-research-actions">
              <Link to={`/saved-research/${item.id}`}>Open</Link>
              <button type="button" disabled={deleting.includes(item.id)}
                onClick={() => handleDelete(item.id, item.title)} aria-label={`Delete ${item.title}`}>
                {deleting.includes(item.id) ? "Deleting..." : "Delete"}
              </button>
            </div>
            {deleteErrors[item.id] && <p className="research-error" role="alert">{deleteErrors[item.id]}</p>}
          </article>)}
        </div>
      </section>
    </main>
  );
}

export default SavedResearch;
