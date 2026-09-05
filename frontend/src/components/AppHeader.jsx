import { Link } from "react-router-dom";
import useAuth from "../auth/useAuth";

function AppHeader() {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const userLabel = user?.display_name?.trim() || user?.email;

  return (
    <header className="app-header">
      <Link className="app-brand" to="/">
        Stock Intelligence
      </Link>

      <nav className="app-nav" aria-label="Account navigation">
        {isLoading ? (
          <span className="app-auth-loading" aria-live="polite">
            Checking session...
          </span>
        ) : isAuthenticated ? (
          <>
            <Link className="app-nav-link" to="/watchlist">
              Watchlist
            </Link>
            <span className="app-user-label" title={user?.email}>
              {userLabel}
            </span>
            <button className="app-nav-button" type="button" onClick={logout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link className="app-nav-link" to="/login">
              Login
            </Link>
            <Link className="app-nav-link app-nav-link-primary" to="/signup">
              Sign Up
            </Link>
          </>
        )}
      </nav>
    </header>
  );
}

export default AppHeader;
