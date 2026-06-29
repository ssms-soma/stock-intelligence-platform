# Architecture

## Overview

AI Stock Intelligence Platform is organized as a FastAPI backend and a React + Vite frontend. The backend exposes stock, news, sentiment, and research endpoints through route modules. Backend services coordinate the current agents, and the frontend consumes those APIs through small API helper modules.

The current research layer is rule-based. LLM/API-based explanation and deeper agentic reasoning are planned, but not currently implemented.

## Backend Architecture

### Routes

Backend routes live under:

- `backend/app/api/routes`

Current route modules:

- `health_routes.py`
  - Health check endpoint.
- `stock_routes.py`
  - Stock metrics endpoint.
  - Stock price history endpoint.
- `news_routes.py`
  - Company or query-based news endpoint.
- `sentiment_routes.py`
  - Sentiment analysis endpoint.
- `research_routes.py`
  - Research summary endpoint.

The FastAPI app is created in:

- `backend/app/main.py`

Routers are included with the `/api` prefix.

### Services

Backend services live under:

- `backend/app/services`

Current service modules:

- `stock_service.py`
- `news_service.py`
- `sentiment_service.py`
- `research_service.py`

Services provide the coordination layer between API routes and agents. They keep route handlers thin and isolate stock, news, sentiment, and research workflows.

### Agents

Backend agents live under:

- `backend/app/agents`

Existing agents:

- `StockDataAgent`
  - Fetches and prepares stock metrics and historical price data.
- `NewsAgent`
  - Fetches company or market news.
- `SentimentAgent`
  - Computes sentiment using TextBlob.
- `ResearchAgent`
  - Produces the current rule-based research summary.

## Frontend Architecture

### Pages

Frontend pages live under:

- `frontend/src/pages`

Current page:

- `Dashboard.jsx`
  - Route-aware page used for both the landing page and stock detail page.
  - Uses React Router params to decide whether it is rendering `/` or `/stock/:ticker`.

### Components

Frontend components live under:

- `frontend/src/components`

Current major components:

- `HeroSection.jsx`
- `MarketTickerTape.jsx`
- `MarketHeadlines.jsx`
- `SearchBar.jsx`
- `StockOverviewCard.jsx`
- `PriceChart.jsx`
- `ResearchSummary.jsx`
- `RelatedCompanies.jsx`
- `NewsSection.jsx`
- `NewsCard.jsx`
- `SentimentBadge.jsx`
- `SkeletonLoader.jsx`

### API Helpers

Frontend API helpers live under:

- `frontend/src/api`

Current API helper modules:

- `stockApi.js`
  - Fetches stock metrics and stock history.
- `newsApi.js`
  - Fetches company or market news.
- `researchApi.js`
  - Fetches the research summary for a ticker.

## Current Data Flow

1. User searches a ticker or clicks a ticker/related company in the frontend.
2. React Router navigates to `/stock/:ticker`.
3. `Dashboard.jsx` reads the ticker from the route params.
4. The frontend calls stock, history, news, and research API helpers.
5. FastAPI routes receive the requests under `/api`.
6. Backend services coordinate the relevant agents.
7. Agents fetch or compute stock data, news, sentiment, and rule-based research output.
8. Backend returns JSON responses.
9. The frontend renders the stock detail dashboard:
   - Stock overview
   - Price chart
   - Research summary
   - Related companies
   - News

## ASCII Architecture Diagram

```text
User
  |
  v
React + Vite Frontend
  |
  |-- / -----------------------> Dashboard landing page
  |                               - HeroSection
  |                               - MarketTickerTape
  |                               - SearchBar
  |                               - MarketHeadlines
  |
  |-- /stock/:ticker ----------> Dashboard stock detail page
                                  - StockOverviewCard
                                  - PriceChart
                                  - ResearchSummary
                                  - RelatedCompanies
                                  - NewsSection

Frontend API Helpers
  |
  |-- stockApi.js -------------> GET /api/stocks/{ticker}
  |                              GET /api/stocks/{ticker}/history
  |
  |-- newsApi.js --------------> GET /api/news/{query}
  |
  |-- researchApi.js ----------> GET /api/research/{ticker}
  |
  v
FastAPI Backend
  |
  |-- Routes ------------------> backend/app/api/routes
  |
  |-- Services ----------------> backend/app/services
  |
  |-- Agents ------------------> backend/app/agents
        |
        |-- StockDataAgent ----> yfinance
        |-- NewsAgent ---------> NewsAPI
        |-- SentimentAgent ----> TextBlob
        |-- ResearchAgent -----> rule-based summary logic
```

## Current Research Layer

The current research summary is rule-based. It combines stock movement, sentiment data, valuation-style fields, and simple signal lists into a structured summary.

Current research output is rendered by:

- `frontend/src/components/ResearchSummary.jsx`

LLM/API-based explanation, deeper reasoning, natural-language justification, and source-grounded analysis are planned but not currently implemented.

## Future Multi-Agent Direction

The planned multi-agent architecture may introduce:

- `RouterAgent`
  - Decides which specialized agents should handle a user request.
- `CompanyAgent`
  - Builds richer company profiles, sector context, and peer comparisons.
- `EventDetectionAgent`
  - Detects major market, earnings, product, regulatory, or news events.
- `LLMAgent`
  - Produces natural-language reasoning and explanation using an LLM.
- `RecommendationAgent`
  - Supports ranking, watchlist suggestions, and recommendation workflows.
- `RAGAgent`
  - Retrieves relevant stored documents, prior summaries, news, filings, or notes.

These agents are planned future work. The current system uses the existing four agents listed above.

## Development Philosophy

- Build core stock intelligence first.
- Add AI reasoning second.
- Add user accounts and persistence third.
- Add social recommendation features last.

