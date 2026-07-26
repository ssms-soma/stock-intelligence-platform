# Architecture

## Overview

AI Stock Intelligence Platform is organized as a FastAPI backend and a React + Vite frontend. The backend exposes market-data, research, search, LLM, RAG, and chat endpoints through route modules. Backend services coordinate specialized agents, and the frontend consumes those APIs through small API helper modules.

The established research summary remains rule-based. Phase 3 adds an isolated provider-neutral LLM layer, deterministic company-name resolution, a request-scoped RAG prototype, a single-turn chat API, and a stock-page AI Research Assistant. These additions do not replace the existing stock and research workflows.

The primary backend layering convention is:

```text
API route
  ↓
Service
  ↓
Agent
  ↓
Provider / external API / deterministic logic
```

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
- `company_routes.py`
  - Company profile endpoint.
- `recommendation_routes.py`
  - Related-company recommendation endpoint.
- `router_routes.py`
  - Deterministic intent-routing endpoint.
- `llm_routes.py`
  - LLM status and isolated prompt-test endpoints.
- `search_routes.py`
  - Company-name and ticker resolution endpoint.
- `rag_routes.py`
  - Request-supplied sample-document RAG test endpoint.
- `chat_routes.py`
  - Single-turn AI research chat endpoint.

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
- `company_service.py`
- `recommendation_service.py`
- `llm_service.py`
- `ticker_resolver_service.py`
- `rag_service.py`
- `chat_service.py`

Services provide the coordination layer between API routes and agents. They keep route handlers thin and isolate stock, news, sentiment, research, search, RAG, and chat workflows.

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
- `CompanyAgent`
  - Builds structured company profile context through yfinance.
- `RecommendationAgent`
  - Produces deterministic related-company suggestions.
- `RouterAgent`
  - Routes supported explicit intents across existing services.
- `TickerResolverAgent`
  - Resolves curated company aliases and preserves ticker-shaped input.
- `LLMAgent`
  - Provides provider-neutral natural-language generation.
- `RAGAgent`
  - Retrieves relevant chunks and builds source metadata.
- `ChatAgent`
  - Selects deterministic chat modes and prepares compact company context.

### LLM Provider Layer

Language-model implementations live under `backend/app/llm`.

```text
LLMAgent
  ↓
LLM provider factory
  ├── NullLLMProvider
  ├── OpenAICompatibleProvider
  └── OllamaProvider
```

Provider selection is environment-driven. The null provider allows safe startup with AI disabled. Ollama supports local development, while the OpenAI-compatible implementation keeps a path open for suitable hosted providers.

### Embedding and RAG Layer

Embedding implementations live under `backend/app/embeddings`:

```text
RAGService
  ↓
Embedding provider factory
  ├── NullEmbeddingProvider
  └── OllamaEmbeddingProvider
```

RAG primitives live under `backend/app/rag`:

- `models.py` defines document, chunk, and retrieval-result contracts.
- `chunker.py` creates deterministic overlapping text chunks.
- `vector_store.py` provides ephemeral in-memory cosine-similarity search.

The current RAG flow is:

```text
Request-supplied sample text
  ↓
TextChunker
  ↓
Embedding provider
  ↓
InMemoryVectorStore
  ↓
RAGAgent
  ↓
LLMAgent
  ↓
Answer plus retriever-owned source metadata
```

The vector store is created per request. No persistent document index, PDF extraction, or filing ingestion exists yet.

### Chat Orchestration

The single-turn chat path is:

```text
chat_routes.py
  ↓
ChatService
  ├── ChatAgent
  ├── LLMAgent
  ├── CompanyService
  └── RAGService
```

`ChatAgent` uses deterministic modes (`auto`, `llm`, `company`, and `rag`); an LLM is not used for routing. Document-backed requests delegate to `RAGService`, so retrieval and citation logic are not duplicated.

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
- `CompanyProfileCard.jsx`
- `AIResearchAssistant.jsx`
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
- `companyApi.js`
  - Fetches company profiles.
- `recommendationApi.js`
  - Fetches related-company recommendations.
- `searchApi.js`
  - Resolves company names or ticker input.
- `chatApi.js`
  - Sends single-turn questions to `/api/chat`.
- `apiCache.js`
  - Provides short-lived frontend request caching for suitable GET workflows.

## Current Data Flow

1. User searches a company name or ticker, or clicks a ticker/related company.
2. Typed search uses `/api/search/resolve`; deterministic ticker selections navigate directly.
3. React Router navigates to `/stock/:ticker`.
4. `Dashboard.jsx` reads the ticker from the route params.
5. The frontend calls stock, history, company, news, recommendation, and research helpers.
6. The AI Research Assistant can send a single-turn ticker-aware request to `/api/chat`.
7. FastAPI routes receive requests under `/api`.
8. Services coordinate the relevant agents and provider abstractions.
9. Backend responses include structured data and warnings where appropriate.
10. The frontend renders the stock detail dashboard:
   - Stock overview
   - Company profile
   - AI Research Assistant
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
                                  - CompanyProfileCard
                                  - AIResearchAssistant
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
  |-- searchApi.js ------------> GET /api/search/resolve
  |
  |-- chatApi.js --------------> POST /api/chat
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
        |-- CompanyAgent ------> yfinance company profile
        |-- TickerResolverAgent -> curated deterministic aliases
        |-- LLMAgent ----------> configured LLM provider
        |-- RAGAgent ----------> in-memory semantic retrieval
        |-- ChatAgent ---------> deterministic chat decisions
```

## Current Research Layer

The current research summary is rule-based. It combines stock movement, sentiment data, valuation-style fields, and simple signal lists into a structured summary.

Current research output is rendered by:

- `frontend/src/components/ResearchSummary.jsx`

The rule-based research endpoint is intentionally separate from Phase 3 chat and RAG. LLM output does not silently replace the existing research summary.

## Key API Endpoints

- `GET /api/health`
- `GET /api/stocks/{ticker}`
- `GET /api/stocks/{ticker}/history`
- `GET /api/news/{query}`
- `POST /api/sentiment`
- `GET /api/research/{ticker}`
- `GET /api/company/{ticker}`
- `GET /api/recommendations/{ticker}`
- `GET /api/router/{ticker}?intent=...`
- `GET /api/llm/status`
- `POST /api/llm/test`
- `GET /api/search/resolve?query=...`
- `POST /api/rag/test`
- `POST /api/chat`

## Local AI Configuration

```env
NEWS_API_KEY=your_news_api_key_here

LLM_PROVIDER=ollama
LLM_MODEL=llama3.1:8b
LLM_BASE_URL=http://localhost:11434
LLM_TIMEOUT=60
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=700

EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_BASE_URL=http://localhost:11434
EMBEDDING_TIMEOUT=60

RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=150
RAG_RETRIEVAL_K=5
```

```powershell
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama list
```

Ollama is used for local development and is not hardcoded into services or agents.

## Current Boundaries

- RAG accepts request-supplied sample documents only.
- No PDF upload, annual-report extraction, or real filing ingestion is implemented.
- Vector storage and chat state are not persistent.
- Chat and the frontend assistant are single-turn.
- The frontend has no RAG document upload interface.
- PostgreSQL, authentication, user accounts, and saved research are not implemented.
- The AI assistant is educational and is not financial advice.

## Roadmap

Near-term:

1. Clean the existing Dashboard lint warnings in an isolated change.
2. Design persistent RAG document indexing.
3. Add one controlled document source.
4. Add RAG-backed document Q&A to the frontend.
5. Add richer stock-, news-, and research-aware chat modes.

Later:

- PostgreSQL
- Authentication and user accounts
- Watchlists and portfolios
- Saved AI research
- Social investing and communities
- Swipe-based stock discovery
- Personalized recommendations

## Development Philosophy

- Build core stock intelligence first.
- Add AI reasoning second.
- Add user accounts and persistence third.
- Add social recommendation features last.

