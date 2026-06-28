function StockOverviewCard({ stockData }) {
  return (
    <div
      style={{ marginTop: "2rem", border: "1px solid #ccc", padding: "1rem" }}
    >
      <h2>{stockData.company_name || stockData.ticker}</h2>

      <p>
        <strong>Ticker:</strong> {stockData.ticker}
      </p>
      <p>
        <strong>Current Price:</strong> {stockData.current_price ?? "N/A"}
      </p>
      <p>
        <strong>Market Cap:</strong> {stockData.market_cap ?? "N/A"}
      </p>
      <p>
        <strong>P/E Ratio:</strong> {stockData.pe_ratio ?? "N/A"}
      </p>
      <p>
        <strong>52 Week High:</strong>{" "}
        {stockData.fifty_two_week_high ?? "N/A"}
      </p>
      <p>
        <strong>52 Week Low:</strong> {stockData.fifty_two_week_low ?? "N/A"}
      </p>
      <p>
        <strong>Volume:</strong> {stockData.volume ?? "N/A"}
      </p>
      <p>
        <strong>Sector:</strong> {stockData.sector ?? "N/A"}
      </p>
    </div>
  );
}

export default StockOverviewCard;
