import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { fetchCompanyProfile } from "../api/companyApi";
import { fetchCompanyNews } from "../api/newsApi";
import { fetchResearchSummary } from "../api/researchApi";
import { fetchStockHistory, fetchStockMetrics } from "../api/stockApi";
import CompanyProfileCard from "../components/CompanyProfileCard";
import HeroSection from "../components/HeroSection";
import MarketHeadlines from "../components/MarketHeadlines";
import MarketTickerTape from "../components/MarketTickerTape";
import NewsSection from "../components/NewsSection";
import PriceChart from "../components/PriceChart";
import RelatedCompanies from "../components/RelatedCompanies";
import ResearchSummary from "../components/ResearchSummary";
import SearchBar from "../components/SearchBar";
import {
  SkeletonCard,
  SkeletonChart,
  SkeletonNewsList,
} from "../components/SkeletonLoader";
import StockOverviewCard from "../components/StockOverviewCard";

function devLog(...args) {
  if (import.meta.env.DEV) {
    console.log(...args);
  }
}

function devWarn(...args) {
  if (import.meta.env.DEV) {
    console.warn(...args);
  }
}

function Dashboard() {
  const navigate = useNavigate();
  const { ticker: routeTicker } = useParams();
  const [ticker, setTicker] = useState("");
  const [selectedTicker, setSelectedTicker] = useState("");
  const [stockData, setStockData] = useState(null);
  const [historyData, setHistoryData] = useState([]);
  const [companyData, setCompanyData] = useState(null);
  const [companyLoading, setCompanyLoading] = useState(false);
  const [companyError, setCompanyError] = useState("");
  const [newsData, setNewsData] = useState([]);
  const [researchData, setResearchData] = useState(null);
  const [researchLoading, setResearchLoading] = useState(false);
  const [researchError, setResearchError] = useState("");
  const [researchRequestId, setResearchRequestId] = useState(0);
  const [chartPeriod, setChartPeriod] = useState("6mo");
  const [loading, setLoading] = useState(false);
  const [stockLoading, setStockLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [stockError, setStockError] = useState("");
  const [historyError, setHistoryError] = useState("");
  const [error, setError] = useState("");
  const requestSequenceRef = useRef(0);
  const historySequenceRef = useRef(0);
  const isStockDetailView = Boolean(routeTicker);

  useEffect(() => {
    devLog("newsData state:", newsData);
  }, [newsData]);

  useEffect(() => {
    if (routeTicker) {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  }, [routeTicker]);

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
        devWarn("failed API name:", "research", err);

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
      setCompanyData(null);
      setCompanyError("");
      setCompanyLoading(false);
      setNewsData([]);
      setResearchData(null);
      setResearchError("");
      setResearchLoading(false);
      setStockError("");
      setHistoryError("");
      setStockLoading(false);
      setHistoryLoading(false);
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

    const requestId = requestSequenceRef.current + 1;
    requestSequenceRef.current = requestId;

    setLoading(true);
    setStockLoading(true);
    setHistoryLoading(true);
    setError("");
    setStockError("");
    setHistoryError("");
    setTicker(trimmedTicker);
    setSelectedTicker(trimmedTicker);
    setStockData(null);
    setHistoryData([]);
    setCompanyData(null);
    setCompanyError("");
    setCompanyLoading(true);
    setNewsData([]);
    setResearchData(null);
    setResearchError("");
    setResearchRequestId((currentId) => currentId + 1);
    setChartPeriod(period);

    fetchCompanyProfile(trimmedTicker)
      .then((companyResult) => {
        if (requestSequenceRef.current !== requestId) {
          return;
        }

        setCompanyData(companyResult?.company_profile || null);
        setCompanyError(companyResult?.warning || "");
      })
      .catch((companyProfileError) => {
        if (requestSequenceRef.current !== requestId) {
          return;
        }

        devWarn("failed API name:", "company profile", companyProfileError);
        setCompanyData(null);
        setCompanyError("Company profile is temporarily unavailable.");
      })
      .finally(() => {
        if (requestSequenceRef.current === requestId) {
          setCompanyLoading(false);
        }
      });

    const [stockResult, historyResult] = await Promise.allSettled([
      fetchStockMetrics(trimmedTicker),
      fetchStockHistory(trimmedTicker, period),
    ]);

    if (requestSequenceRef.current !== requestId) {
      return;
    }

    devLog("ticker:", trimmedTicker);
    devLog("stock API status:", stockResult.status);

    let newsQuery = trimmedTicker;

    if (stockResult.status === "fulfilled") {
      const data = stockResult.value && typeof stockResult.value === "object"
        ? stockResult.value
        : null;
      setStockData(data);

      if (!data) {
        setStockError("Stock metrics are temporarily unavailable.");
      }

      newsQuery = data?.company_name && data.company_name !== "N/A"
        ? data.company_name
        : trimmedTicker;
    } else {
      devWarn("failed API name:", "stock metrics", stockResult.reason);
      setStockError("Stock metrics are temporarily unavailable.");
    }

    if (historyResult.status === "fulfilled") {
      const history = Array.isArray(historyResult.value) ? historyResult.value : [];
      setHistoryData(history);
      devLog("history length:", history.length);
      devLog("first history row:", history[0]);
    } else {
      devWarn("failed API name:", "stock history", historyResult.reason);
      setHistoryError("Price history is temporarily unavailable.");
      setHistoryData([]);
    }

    setStockLoading(false);
    setHistoryLoading(false);

    try {
      const news = await fetchCompanyNews(newsQuery);

      if (requestSequenceRef.current !== requestId) {
        return;
      }

      devLog("Parsed news API response:", news);
      setNewsData(Array.isArray(news) ? news : []);
    } catch (newsError) {
      if (requestSequenceRef.current !== requestId) {
        return;
      }

      devWarn("failed API name:", "company news", newsError);
      setNewsData([]);
    } finally {
      if (requestSequenceRef.current === requestId) {
        setLoading(false);
      }
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
    setHistoryLoading(true);
    setHistoryError("");
    const historyRequestId = historySequenceRef.current + 1;
    historySequenceRef.current = historyRequestId;

    try {
      const history = await fetchStockHistory(selectedTicker, period);

      if (historySequenceRef.current !== historyRequestId) {
        return;
      }

      const safeHistory = Array.isArray(history) ? history : [];
      setHistoryData(safeHistory);
      devLog("ticker:", selectedTicker);
      devLog("history length:", safeHistory.length);
      devLog("first history row:", safeHistory[0]);
    } catch (err) {
      if (historySequenceRef.current !== historyRequestId) {
        return;
      }

      devWarn("failed API name:", "stock history", err);
      setHistoryError("Unable to fetch price history for this period.");
      setHistoryData([]);
    } finally {
      if (historySequenceRef.current === historyRequestId) {
        setHistoryLoading(false);
      }
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
          {error && <p style={{ marginTop: "2rem", color: "red" }}>{error}</p>}

          {stockError && (
            <p style={{ marginTop: "2rem", color: "#b91c1c" }}>{stockError}</p>
          )}

          {stockLoading && !stockData && <SkeletonCard />}

          {stockData && <StockOverviewCard stockData={stockData} />}

          <CompanyProfileCard
            profile={companyData}
            loading={companyLoading}
            error={companyError}
          />

          {historyLoading && historyData.length === 0 && <SkeletonChart />}

          {!historyLoading && (
            <PriceChart
              historyData={historyData}
              activePeriod={chartPeriod}
              onPeriodChange={handlePeriodChange}
              error={historyError}
              ticker={selectedTicker}
              priceTarget={companyData?.price_target}
              marketMetadata={stockData || companyData}
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

          {loading && newsData.length === 0 && <SkeletonNewsList />}

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
