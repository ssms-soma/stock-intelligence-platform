import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";

function NotFound() {
  return (
    <div
      style={{
        minHeight: "100svh",
        padding: "2rem",
        background: "#f8fafc",
        color: "#0f172a",
        fontFamily: "Arial",
        textAlign: "left",
      }}
    >
      <h1 style={{ marginTop: 0, fontSize: "2rem", letterSpacing: "0" }}>
        Page not found
      </h1>
      <p style={{ color: "#475569" }}>
        The page you are looking for does not exist.
      </p>
      <Link
        to="/"
        style={{
          display: "inline-block",
          marginTop: "1rem",
          color: "#2563eb",
          fontWeight: 700,
        }}
      >
        Back to market overview
      </Link>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard key="landing" />} />
        <Route
          path="/stock/:ticker"
          element={<Dashboard key="stock-detail" />}
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
