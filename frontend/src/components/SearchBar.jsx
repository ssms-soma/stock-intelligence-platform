function SearchBar({ ticker, onTickerChange, onSearch }) {
  return (
    <div>
      <input
        type="text"
        placeholder="Enter ticker, e.g. AAPL or INFY.NS"
        value={ticker}
        onChange={(e) => onTickerChange(e.target.value)}
        style={{ padding: "0.7rem", width: "300px", marginRight: "1rem" }}
      />

      <button onClick={onSearch} style={{ padding: "0.7rem 1rem" }}>
        Search
      </button>
    </div>
  );
}

export default SearchBar;
