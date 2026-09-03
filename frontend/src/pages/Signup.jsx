import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { AuthApiError } from "../api/authApi";
import useAuth from "../auth/useAuth";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function getSignupError(error) {
  if (error?.accountCreated) {
    return "Your account was created, but automatic login failed. Please log in.";
  }

  if (error instanceof AuthApiError) {
    if (error.status === 409) return "An account with this email already exists.";
    if (error.status === 422) return "Please check the information you entered.";
    if (error.status === null) return error.message;
  }

  if (error instanceof TypeError) {
    return "Unable to reach the server. Please try again.";
  }

  return "Unable to create your account right now. Please try again.";
}

function Signup() {
  const navigate = useNavigate();
  const { isAuthenticated, isLoading, register } = useAuth();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (isLoading) {
    return <main className="auth-page"><p>Checking your session...</p></main>;
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    const normalizedEmail = email.trim();

    if (!normalizedEmail) {
      setError("Email is required.");
      return;
    }

    if (!EMAIL_PATTERN.test(normalizedEmail)) {
      setError("Enter a valid email address.");
      return;
    }

    if (displayName.trim().length > 100) {
      setError("Display name must be 100 characters or fewer.");
      return;
    }

    if (password.length < 8 || password.length > 128) {
      setError("Password must be between 8 and 128 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);

    try {
      await register({ email: normalizedEmail, password, displayName });
      navigate("/", { replace: true });
    } catch (requestError) {
      setError(getSignupError(requestError));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="signup-title">
        <p className="auth-eyebrow">Create your account</p>
        <h1 id="signup-title">Sign Up</h1>
        <p className="auth-intro">Start building your personalized research workspace.</p>

        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <label htmlFor="signup-name">Display name <span>(optional)</span></label>
          <input
            id="signup-name"
            type="text"
            autoComplete="name"
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
            disabled={submitting}
            maxLength={100}
          />

          <label htmlFor="signup-email">Email</label>
          <input
            id="signup-email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            disabled={submitting}
            maxLength={320}
            required
          />

          <label htmlFor="signup-password">Password</label>
          <input
            id="signup-password"
            type="password"
            autoComplete="new-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            disabled={submitting}
            minLength={8}
            maxLength={128}
            required
          />

          <label htmlFor="signup-confirm-password">Confirm password</label>
          <input
            id="signup-confirm-password"
            type="password"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            disabled={submitting}
            minLength={8}
            maxLength={128}
            required
          />

          {error && <p className="auth-error" role="alert">{error}</p>}

          <button className="auth-submit" type="submit" disabled={submitting}>
            {submitting ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="auth-switch">
          Already have an account? <Link to="/login">Login</Link>
        </p>
      </section>
    </main>
  );
}

export default Signup;
