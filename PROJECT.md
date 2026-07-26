# AI Stock Intelligence Platform

## Description

AI Stock Intelligence Platform is a full-stack stock research dashboard that combines market data, historical price charts, company intelligence, news, sentiment analysis, related companies, rule-based research, and an optional AI research assistant in a React frontend backed by FastAPI.

Phase 3 adds provider-neutral language-model and embedding foundations, local Ollama support, deterministic company-name search, a backend RAG prototype, and a single-turn AI chat workflow. The platform is under local development and is not presented as production-deployed or as a source of financial advice.

## Current Tech Stack

- FastAPI backend
- React + Vite frontend
- yfinance for stock metrics and historical price data
- NewsAPI for company and market news
- TextBlob for sentiment analysis
- Recharts for price charts
- React Router for frontend routing
- Provider-neutral LLM and embedding interfaces
- Ollama for optional local chat and embedding models
- Pure-Python in-memory cosine-similarity retrieval for the RAG prototype

## Completed Features

- Stock metrics lookup
- Stock price history lookup
- Market ticker tape
- Company news
- Company profiles
- Sentiment analysis
- Rule-based research summary
- Research frontend section
- Related companies
- Deterministic company-name and ticker resolution
- Google Finance-style chart periods:
  - 1D
  - 5D
  - 1M
  - 6M
- Frontend route-based stock detail pages
- Loading skeletons for stock detail content
- Fintech-style stock overview, news cards, sentiment badges, related company cards, and research summary cards
- Provider-neutral LLM support with null, OpenAI-compatible, and Ollama providers
- Provider-neutral embeddings with null and Ollama providers
- Request-scoped RAG testing over supplied sample text
- Single-turn backend AI chat modes
- Stock-page AI Research Assistant

## Phase 3 AI Foundation

### LLM providers

Language-model access is isolated behind a provider interface and selected through environment configuration.

- The null provider keeps AI functionality safely disabled when no provider is configured.
- The OpenAI-compatible provider supports compatible hosted APIs.
- The Ollama provider supports local chat development without an API key.
- Provider failures return structured warnings instead of crashing established stock workflows.

The abstraction is intended to allow later deployment through an appropriate hosted provider, such as an OpenAI-compatible Gemini or OpenRouter configuration, without coupling application services to Ollama.

### Company-name search

`GET /api/search/resolve?query=...` provides deterministic company-name resolution before stock navigation. Examples include:

- Infosys → `INFY.NS`
- Reliance → `RELIANCE.NS`
- TCS or Tata Consultancy → `TCS.NS`
- Apple → `AAPL`
- Microsoft → `MSFT`

Exact ticker input remains supported. Normal search does not use an LLM.

### RAG test slice

The backend RAG prototype includes:

- Provider-neutral embedding contracts
- Null and Ollama embedding providers
- Local `nomic-embed-text` support
- Deterministic overlapping text chunks
- Ephemeral, request-scoped vector storage
- Pure-Python cosine-similarity retrieval
- `RAGAgent` retrieval and source construction
- `RAGService` orchestration
- `POST /api/rag/test`

The endpoint accepts sample document text in its request. It does not ingest PDFs, filings, or persisted document collections.

### AI chat

`POST /api/chat` is a single-turn backend chat foundation with deterministic modes:

- `auto`
- `llm`
- `company`
- `rag`

`ChatService` coordinates `ChatAgent`, `LLMAgent`, `CompanyService`, and `RAGService`. Document-backed chat delegates to the existing RAG workflow, while ticker-based chat can use a compact company profile.

The stock-detail frontend includes `AIResearchAssistant.jsx`. It sends the current ticker to `/api/chat` in `auto` mode and provides quick prompts, loading feedback, structured warnings, and friendly request errors.

## Current Routes

### Frontend Routes

- `/`
  - Market overview landing page.
  - Shows hero section, ticker tape, stock search, and market headlines.

- `/stock/:ticker`
  - Stock detail page for a selected ticker.
  - Shows stock overview, company profile, AI Research Assistant, price chart, research summary, related companies, and news.

### Backend API Routes

The backend currently mounts API routers under `/api`.

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

Add the following values to `backend/.env` for local Ollama chat and RAG testing:

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

Pull and verify the local models:

```powershell
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama list
```

Ollama is a local development option, not a hard dependency of the architecture. Setting the null providers keeps AI functionality safely disabled.

## Running and Validation

Backend:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm.cmd run dev
```

Backend tests:

```powershell
cd backend
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Frontend production build:

```powershell
cd frontend
npm.cmd run build
```

## Current Limitations

- RAG accepts request-supplied sample text only.
- PDF uploads, annual-report extraction, and filing ingestion are not implemented.
- Vector storage is ephemeral and is rebuilt per RAG request.
- PostgreSQL and persistent document indexing are not implemented.
- User authentication and user accounts are not implemented.
- Chat and the frontend assistant are single-turn and have no persistent history.
- The frontend assistant currently uses ticker-based company context; it has no document upload or RAG-source UI.
- Stock/news/research-aware chat modes beyond the current company and supplied-document contexts are not implemented.
- Ollama is intended for local development; a hosted provider can be configured for a future deployment.
- The platform provides educational research tooling, not financial advice.

## Future Roadmap

Near-term engineering work:

1. Fix the existing `Dashboard.jsx` lint warnings in a separate, focused change.
2. Design persistent RAG document indexing.
3. Add one controlled document source type.
4. Add a RAG-backed document question-and-answer UI.
5. Add richer stock-, news-, and research-aware chat modes.

Later product work:

- PostgreSQL persistence
- Authentication and user accounts
- Watchlists and portfolios
- Saved AI research
- Social investing features
- Communities and discussions
- Swipe-based stock discovery
- Personalized recommendations
- Production deployment planning

## Development Philosophy

- Build core stock intelligence first.
- Add AI reasoning second.
- Add user accounts and persistence third.
- Add social recommendation features last.

