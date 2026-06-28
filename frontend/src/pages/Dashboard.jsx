import { useEffect, useState } from "react";
import { fetchCompanyNews } from "../api/newsApi";
import { fetchStockHistory, fetchStockMetrics } from "../api/stockApi";
import NewsSection from "../components/NewsSection";
import PriceChart from "../components/PriceChart";
import SearchBar from "../components/SearchBar";
import StockOverviewCard from "../components/StockOverviewCard";

function Dashboard() {
  const [ticker, setTicker] = useState("");
  const [stockData, setStockData] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [newsData, setNewsData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    console.log("newsData state:", newsData);
  }, [newsData]);

  const fetchStockData = async () => {
    if (!ticker.trim()) {
      setError("Please enter a ticker symbol");
      return;
    }

    setLoading(true);
    setError("");
    setStockData(null);
    setHistoryData([]);
    setNewsData([]);

    try {
      const trimmedTicker = ticker.trim();

      const [data, history] = await Promise.all([
        fetchStockMetrics(trimmedTicker),
        fetchStockHistory(trimmedTicker),
      ]);
      const newsQuery = data.company_name || trimmedTicker;

      setStockData(data);
      setHistoryData(history);

      try {
        const news = await fetchCompanyNews(newsQuery);

        console.log("Parsed news API response:", news);
        setNewsData(Array.isArray(news) ? news : []);
      } catch (newsError) {
        console.warn("News fetch error:", newsError);
        setNewsData([]);
      }
    } catch (err) {
      console.error("Fetch error:", err);
      setError("Unable to fetch stock data or news. Check ticker or backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>AI Stock Intelligence Platform</h1>

      <SearchBar
        ticker={ticker}
        onTickerChange={setTicker}
        onSearch={fetchStockData}
      />

      {loading && <p>Loading stock data...</p>}

      {error && <p style={{ color: "red" }}>{error}</p>}

      {stockData && <StockOverviewCard stockData={stockData} />}

      {historyData.length > 0 && <PriceChart historyData={historyData} />}

      {Array.isArray(newsData) && newsData.length > 0 && (
        <NewsSection newsData={newsData} />
      )}

      {stockData && Array.isArray(newsData) && newsData.length === 0 && !loading && (
        <p style={{ marginTop: "3rem" }}>
          No news articles found for this stock.
        </p>
      )}
    </div>
  );
}

export default Dashboard;
