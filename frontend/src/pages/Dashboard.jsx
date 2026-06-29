import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { fetchCompanyNews } from "../api/newsApi";
import { fetchResearchSummary } from "../api/researchApi";
import { fetchStockHistory, fetchStockMetrics } from "../api/stockApi";
import HeroSection from "../components/HeroSection";
import MarketHeadlines from "../components/MarketHeadlines";
import MarketTickerTape from "../components/MarketTickerTape";
import NewsSection from "../components/NewsSection";
import PriceChart from "../components/PriceChart";
import RelatedCompanies from "../components/RelatedCompanies";
import ResearchSummary from "../components/ResearchSummary";
import SearchBar from "../components/SearchBar";
import StockOverviewCard from "../components/StockOverviewCard";

function Dashboard() {
  const navigate = useNavigate();
  const { ticker: routeTicker } = useParams();
  const [ticker, setTicker] = useState("");
  const [selectedTicker, setSelectedTicker] = useState("");
  const [stockData, setStockData] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [newsData, setNewsData] = useState([]);
  const [researchData, setResearchData] = useState(null);
  const [researchLoading, setResearchLoading] = useState(false);
  const [researchError, setResearchError] = useState("");
  const [researchRequestId, setResearchRequestId] = useState(0);
  const [chartPeriod, setChartPeriod] = useState("6mo");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const isStockDetailView = Boolean(routeTicker);

  useEffect(() => {
    console.log("newsData state:", newsData);
  }, [newsData]);

  useEffect(() => {
    let isCurrent = true;

    async function loadResearchSummary() {
      if (!selectedTicker) {
        setResearchData(null);
        setResearchError("");
        setResearchLoading(false);
        return;
      }

      setResearchLoading(true);
      setResearchError("");
      setResearchData(null);

      try {
        const data = await fetchResearchSummary(selectedTicker);

        if (isCurrent) {
          setResearchData(data);
        }
      } catch (err) {
        console.error("Research fetch error:", err);

        if (isCurrent) {
          setResearchError("Unable to fetch AI research summary.");
        }
      } finally {
        if (isCurrent) {
          setResearchLoading(false);
        }
      }
    }

    loadResearchSummary();

    return () => {
      isCurrent = false;
    };
  }, [selectedTicker, researchRequestId]);

  useEffect(() => {
    if (!routeTicker) {
      setSelectedTicker("");
      setStockData(null);
      setHistoryData([]);
      setNewsData([]);
      setResearchData(null);
      setResearchError("");
      setResearchLoading(false);
      setChartPeriod("6mo");
      return;
    }

    fetchStockData("6mo", routeTicker);
  }, [routeTicker]);

  const navigateToStock = (requestedTicker = ticker) => {
    const trimmedTicker = requestedTicker.trim();

    if (!trimmedTicker) {
      setError("Please enter a ticker symbol");
      return;
    }

    setError("");

    if (
      isStockDetailView &&
      routeTicker?.toUpperCase() === trimmedTicker.toUpperCase()
    ) {
      fetchStockData("6mo", trimmedTicker);
      return;
    }

    navigate(`/stock/${encodeURIComponent(trimmedTicker)}`);
  };

  const fetchStockData = async (period = chartPeriod, requestedTicker) => {
    const trimmedTicker = requestedTicker.trim();

    if (!trimmedTicker) {
      setError("Please enter a ticker symbol");
      return;
    }

    setLoading(true);
    setError("");
    setTicker(trimmedTicker);
    setStockData(null);
    setHistoryData([]);
    setNewsData([]);
    setResearchData(null);
    setResearchError("");

    try {
      const [data, history] = await Promise.all([
        fetchStockMetrics(trimmedTicker),
        fetchStockHistory(trimmedTicker, period),
      ]);
      const newsQuery = data.company_name || trimmedTicker;

      setStockData(data);
      setHistoryData(history);
      setSelectedTicker(trimmedTicker);
      setResearchRequestId((currentId) => currentId + 1);
      setChartPeriod(period);

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

  const handleTickerSelect = (nextTicker) => {
    navigateToStock(nextTicker);
  };

  const handlePeriodChange = async (period) => {
    if (!selectedTicker) {
      return;
    }

    setChartPeriod(period);

    try {
      const history = await fetchStockHistory(selectedTicker, period);
      setHistoryData(history);
    } catch (err) {
      console.error("History fetch error:", err);
      setError("Unable to fetch price history for this period.");
    }
  };

  const goToLanding = () => {
    setError("");
    navigate("/");
  };

  const renderSearchBox = () => (
    <section
      style={{
        margin: "2rem auto 0",
        maxWidth: "720px",
        padding: "1.25rem",
        border: "1px solid #dbe3ef",
        background: "#ffffff",
        boxShadow: "0 8px 24px rgba(15, 23, 42, 0.06)",
      }}
    >
      <SearchBar
        ticker={ticker}
        onTickerChange={setTicker}
        onSearch={() => navigateToStock(ticker)}
      />
    </section>
  );

  if (isStockDetailView) {
    return (
      <div
        style={{
          flex: 1,
          minHeight: "100svh",
          width: "100%",
          background: "#f8fafc",
          fontFamily: "Arial",
        }}
      >
        <header
          style={{
            padding: "1.25rem 2rem",
            borderBottom: "1px solid #dbe3ef",
            background: "#ffffff",
            textAlign: "left",
          }}
        >
          <button
            onClick={goToLanding}
            style={{
              marginBottom: "1rem",
              border: "none",
              background: "transparent",
              color: "#2563eb",
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            Back to market overview
          </button>

          <h1
            style={{
              margin: "0 0 1rem",
              color: "#0f172a",
              fontSize: "2rem",
              letterSpacing: "0",
            }}
          >
            {stockData?.company_name || selectedTicker || routeTicker}
          </h1>

          <SearchBar
            ticker={ticker}
            onTickerChange={setTicker}
            onSearch={() => navigateToStock(ticker)}
          />
        </header>

        <main style={{ padding: "0 2rem 2rem" }}>
          {loading && (
            <p style={{ marginTop: "2rem" }}>Loading stock data...</p>
          )}

          {error && <p style={{ marginTop: "2rem", color: "red" }}>{error}</p>}

          {stockData && <StockOverviewCard stockData={stockData} />}

          {historyData.length > 0 && (
            <PriceChart
              historyData={historyData}
              activePeriod={chartPeriod}
              onPeriodChange={handlePeriodChange}
            />
          )}

          {(selectedTicker || researchLoading || researchError) && (
            <ResearchSummary
              ticker={selectedTicker}
              researchData={researchData}
              loading={researchLoading}
              error={researchError}
            />
          )}

          <RelatedCompanies
            ticker={selectedTicker}
            onTickerSelect={handleTickerSelect}
          />

          {Array.isArray(newsData) && newsData.length > 0 && (
            <NewsSection newsData={newsData} />
          )}

          {stockData &&
            Array.isArray(newsData) &&
            newsData.length === 0 &&
            !loading && (
              <p style={{ marginTop: "3rem" }}>
                No news articles found for this stock.
              </p>
            )}
        </main>
      </div>
    );
  }

  return (
    <div
      style={{
        flex: 1,
        minHeight: "100svh",
        width: "100%",
        paddingBottom: "2rem",
        fontFamily: "Arial",
        background: "#f8fafc",
      }}
    >
      <HeroSection />
      <MarketTickerTape onTickerSelect={handleTickerSelect} />

      <main style={{ padding: "0 2rem 2rem" }}>
        {renderSearchBox()}

        <MarketHeadlines />

        {loading && <p>Loading stock data...</p>}

        {error && <p style={{ color: "red" }}>{error}</p>}
      </main>
    </div>
  );
}

export default Dashboard;
