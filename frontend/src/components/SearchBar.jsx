function SearchBar({ ticker, onTickerChange, onSearch, searching = false }) {
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        onSearch();
      }}
      style={{
        display: "flex",
        justifyContent: "center",
        gap: "0.75rem",
        width: "100%",
      }}
    >
      <input
        type="text"
        placeholder="Enter company or ticker, e.g. Infosys or AAPL"
        value={ticker}
        onChange={(e) => onTickerChange(e.target.value)}
        disabled={searching}
        style={{
          boxSizing: "border-box",
          flex: "1 1 280px",
          maxWidth: "440px",
          padding: "0.85rem 1rem",
          border: "1px solid #cbd5e1",
          borderRadius: "4px",
          background: "#ffffff",
          color: "#0f172a",
          fontSize: "1rem",
        }}
      />

      <button
        type="submit"
        disabled={searching}
        style={{
          padding: "0.85rem 1.2rem",
          border: "1px solid #0f172a",
          borderRadius: "4px",
          background: "#0f172a",
          color: "#ffffff",
          fontWeight: 700,
          cursor: searching ? "wait" : "pointer",
          opacity: searching ? 0.7 : 1,
        }}
      >
        {searching ? "Searching..." : "Search"}
      </button>
    </form>
  );
}

export default SearchBar;
