import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { saveResearch } from "../api/savedResearchApi";
import useAuth from "../auth/useAuth";

function SaveResearchButton({ ticker, content }) {
  const { token, isAuthenticated, isLoading, logout } = useAuth();
  // Remount local mutation state when the authenticated session changes.
  return <SaveControl key={token || "anonymous"} {...{
    ticker, content, token, isAuthenticated, isLoading, logout,
  }} />;
}

function SaveControl({ ticker, content, token, isAuthenticated, isLoading, logout }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [saved, setSaved] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const controllerRef = useRef(null);

  useEffect(() => {
    return () => controllerRef.current?.abort();
  }, []);

  async function handleSave() {
    if (controllerRef.current && !controllerRef.current.signal.aborted) return;
    if (!isAuthenticated || !token) {
      navigate("/login", { state: { from: location.pathname } });
      return;
    }
    const controller = new AbortController();
    controllerRef.current = controller;
    setPending(true);
    setError("");
    try {
      await saveResearch(token, ticker, content, { signal: controller.signal });
      if (!controller.signal.aborted) setSaved(true);
    } catch (requestError) {
      if (controller.signal.aborted) return;
      if (requestError.status === 401) {
        logout();
        navigate("/login", { state: { from: location.pathname } });
        return;
      }
      setError("Could not save research. Please try again.");
    } finally {
      if (!controller.signal.aborted) {
        controllerRef.current = null;
        setPending(false);
      }
    }
  }

  return (
    <div className="saved-research-control">
      <button className={`watchlist-button${saved && !pending ? " is-saved" : ""}`} type="button" onClick={handleSave}
        disabled={isLoading || pending || saved || !ticker}
        aria-live="polite">
        {pending ? "Saving..." : saved ? "Saved" : "Save Research"}
      </button>
      {error && <span className="watchlist-control-error" role="alert">{error}</span>}
    </div>
  );
}

export default SaveResearchButton;
