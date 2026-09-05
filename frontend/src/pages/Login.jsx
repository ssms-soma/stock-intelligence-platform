import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { AuthApiError } from "../api/authApi";
import useAuth from "../auth/useAuth";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function getLoginError(error) {
  if (error instanceof AuthApiError) {
    if (error.status === 401) return "Invalid email or password.";
    if (error.status === 422) return "Please check your email and password.";
    if (error.status === null) return error.message;
  }

  if (error instanceof TypeError) {
    return "Unable to reach the server. Please try again.";
  }

  return "Unable to sign in right now. Please try again.";
}

function Login() {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const requestedPath = location.state?.from;
  const returnPath =
    typeof requestedPath === "string" &&
    requestedPath.startsWith("/") &&
    !requestedPath.startsWith("//")
      ? requestedPath
      : "/";

  if (isLoading) {
    return <main className="auth-page"><p>Checking your session...</p></main>;
  }

  if (isAuthenticated) {
    return <Navigate to={returnPath} replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");

    if (!email.trim()) {
      setError("Email is required.");
      return;
    }

    if (!EMAIL_PATTERN.test(email.trim())) {
      setError("Enter a valid email address.");
      return;
    }

    if (!password) {
      setError("Password is required.");
      return;
    }

    setSubmitting(true);

    try {
      await login({ email, password });
      navigate(returnPath, { replace: true });
    } catch (requestError) {
      setError(getLoginError(requestError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="login-title">
        <p className="auth-eyebrow">Welcome back</p>
        <h1 id="login-title">Login</h1>
        <p className="auth-intro">Sign in to your Stock Intelligence account.</p>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <label htmlFor="login-email">Email</label>
          <input
            id="login-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            disabled={submitting}
            maxLength={320}
            required
          />

          <label htmlFor="login-password">Password</label>
          <input
            id="login-password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            disabled={submitting}
            maxLength={128}
            required
          />

          {error && <p className="auth-error" role="alert">{error}</p>}

          <button className="auth-submit" type="submit" disabled={submitting}>
            {submitting ? "Signing in..." : "Login"}
          </button>
        </form>

        <p className="auth-switch">
          New to Stock Intelligence? <Link to="/signup">Create an account</Link>
        </p>
      </section>
    </main>
  );
}

export default Login;
