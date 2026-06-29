function StockOverviewCard({ stockData }) {
  return (
    <div
      style={{
        marginTop: "2rem",
        border: "1px solid #dbe3ef",
        padding: "1rem",
        background: "#ffffff",
        color: "#475569",
      }}
    >
      <h2 style={{ color: "#0f172a" }}>
        {stockData.company_name || stockData.ticker}
      </h2>

      <p>
        <strong style={{ color: "#0f172a" }}>Ticker:</strong> {stockData.ticker}
      </p>
      <p>
        <strong style={{ color: "#0f172a" }}>Current Price:</strong>{" "}
        {stockData.current_price ?? "N/A"}
      </p>
      <p>
        <strong style={{ color: "#0f172a" }}>Market Cap:</strong>{" "}
        {stockData.market_cap ?? "N/A"}
      </p>
      <p>
        <strong style={{ color: "#0f172a" }}>P/E Ratio:</strong>{" "}
        {stockData.pe_ratio ?? "N/A"}
      </p>
      <p>
        <strong style={{ color: "#0f172a" }}>52 Week High:</strong>{" "}
        {stockData.fifty_two_week_high ?? "N/A"}
      </p>
      <p>
        <strong style={{ color: "#0f172a" }}>52 Week Low:</strong>{" "}
        {stockData.fifty_two_week_low ?? "N/A"}
      </p>
      <p>
        <strong style={{ color: "#0f172a" }}>Volume:</strong>{" "}
        {stockData.volume ?? "N/A"}
      </p>
      <p>
        <strong style={{ color: "#0f172a" }}>Sector:</strong>{" "}
        {stockData.sector ?? "N/A"}
      </p>
    </div>
  );
}

export default StockOverviewCard;
