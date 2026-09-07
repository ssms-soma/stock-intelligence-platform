import { useEffect, useState } from "react";
import { Link, Navigate, useLocation, useParams } from "react-router-dom";
import { fetchSavedResearchDetail } from "../api/savedResearchApi";
import useAuth from "../auth/useAuth";
import ResearchSummary from "../components/ResearchSummary";

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

function SavedResearchDetail() {
  const { id } = useParams();
  const location = useLocation();
  const { token, isAuthenticated, isLoading, logout } = useAuth();
  if (isLoading) return <main className="watchlist-page">Checking your session...</main>;
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <SavedDetail key={`${token}:${id}`} {...{ id, token, logout }} />;
}

function SavedDetail({ id, token, logout }) {
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notFound, setNotFound] = useState(false);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    fetchSavedResearchDetail(token, id, { signal: controller.signal })
      .then((data) => {
        if (!controller.signal.aborted) setItem(data);
      })
      .catch((requestError) => {
        if (controller.signal.aborted) return;
        if (requestError.status === 401) return logout();
        if (requestError.status === 404) setNotFound(true);
        else setError("Unable to load saved research. Please try again.");
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [id, logout, retry, token]);

  return <main className="watchlist-page">
    <div className="saved-research-detail">
      <Link to="/saved-research">Back to Saved Research</Link>
      {loading && <p aria-live="polite">Loading saved research...</p>}
      {notFound && <p role="status">Saved research not found.</p>}
      {error && <div className="watchlist-error" role="alert">
        <p>{error}</p><button type="button" onClick={() => {
          setLoading(true); setError(""); setRetry((value) => value + 1);
        }}>Retry</button>
      </div>}
      {item && <>
        <h1>{item.title}</h1>
        <p className="watchlist-intro">Saved <time dateTime={item.created_at}>
          {formatSavedDate(item.created_at)}
        </time></p>
        <ResearchSummary ticker={item.ticker} researchData={{ research_summary: item.content }} allowSave={false} />
      </>}
    </div>
  </main>;
}

export default SavedResearchDetail;
