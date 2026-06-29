function HeroSection() {
  return (
    <section
      style={{
        padding: "3.75rem 2rem 2.5rem",
        textAlign: "left",
        background: "#f8fafc",
        color: "#0f172a",
        borderBottom: "1px solid #dbe3ef",
      }}
    >
      <div style={{ maxWidth: "980px", margin: "0 auto" }}>
        <p
          style={{
            marginBottom: "0.75rem",
            color: "#2563eb",
            fontSize: "0.82rem",
            fontWeight: 700,
            textTransform: "uppercase",
            letterSpacing: "0",
          }}
        >
          Market intelligence dashboard
        </p>

        <h1
          style={{
            margin: "0 0 1rem",
            color: "#0f172a",
            fontSize: "clamp(2.4rem, 6vw, 4.5rem)",
            lineHeight: 1,
            letterSpacing: "0",
            fontWeight: 800,
          }}
        >
          AI Stock Intelligence Platform
        </h1>

        <p
          style={{
            maxWidth: "720px",
            marginBottom: "1.25rem",
            color: "#475569",
            fontSize: "1.1rem",
            lineHeight: 1.6,
          }}
        >
          Track stocks, news sentiment, price trends, and research insights in
          one place.
        </p>

        <p
          style={{
            display: "inline-block",
            padding: "0.45rem 0.65rem",
            color: "#475569",
            fontSize: "0.82rem",
            border: "1px solid #cbd5e1",
            background: "#ffffff",
          }}
        >
          Research and educational use only. Not financial advice.
        </p>
      </div>
    </section>
  );
}

export default HeroSection;
