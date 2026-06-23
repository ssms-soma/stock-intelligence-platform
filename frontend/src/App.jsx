import { useState } from "react";

function App() {
  const [ticker, setTicker] = useState("");
  const [stockData, setStockData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchStockData = async () => {
    if (!ticker.trim()) {
      setError("Please enter a ticker symbol");
      return;
    }

    setLoading(true);
    setError("");
    setStockData(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/stocks/${ticker.trim()}`
      );

      if (!response.ok) {
        throw new Error("Failed to fetch stock data");
      }

      const data = await response.json();
      setStockData(data);
    } catch (err) {
      setError("Unable to fetch stock data. Check ticker or backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>AI Stock Intelligence Platform</h1>

      <div>
        <input
          type="text"
          placeholder="Enter ticker, e.g. AAPL or INFY.NS"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          style={{ padding: "0.7rem", width: "300px", marginRight: "1rem" }}
        />

        <button onClick={fetchStockData} style={{ padding: "0.7rem 1rem" }}>
          Search
        </button>
      </div>

      {loading && <p>Loading stock data...</p>}

      {error && <p style={{ color: "red" }}>{error}</p>}

      {stockData && (
        <div style={{ marginTop: "2rem", border: "1px solid #ccc", padding: "1rem" }}>
          <h2>{stockData.company_name || stockData.ticker}</h2>

          <p><strong>Ticker:</strong> {stockData.ticker}</p>
          <p><strong>Current Price:</strong> {stockData.current_price ?? "N/A"}</p>
          <p><strong>Market Cap:</strong> {stockData.market_cap ?? "N/A"}</p>
          <p><strong>P/E Ratio:</strong> {stockData.pe_ratio ?? "N/A"}</p>
          <p><strong>52 Week High:</strong> {stockData.fifty_two_week_high ?? "N/A"}</p>
          <p><strong>52 Week Low:</strong> {stockData.fifty_two_week_low ?? "N/A"}</p>
          <p><strong>Volume:</strong> {stockData.volume ?? "N/A"}</p>
          <p><strong>Sector:</strong> {stockData.sector ?? "N/A"}</p>
        </div>
      )}
    </div>
  );
}

export default App;