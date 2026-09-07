# Architecture

## System Boundaries

React/Vite consumes FastAPI endpoints under `/api`. Public intelligence and AI/document workflows coexist with authenticated PostgreSQL user data.

```text
React + React Router
  ├── Public dashboard and stock detail
  ├── AIResearchAssistant: chat and document Q&A
  └── AuthContext: login, Watchlist, Saved Research
         |
         v
FastAPI routes
  ├── Intelligence services → agents → providers / rules
  ├── Document service → extraction → RAG → generation
  └── get_current_user → persistence services → SQLAlchemy → PostgreSQL
```

Routes stay thin. Intelligence services orchestrate agents; persistence services use database sessions directly. Not every endpoint requires an agent.

## Backend Organization

| Directory | Responsibility |
|---|---|
| `app/api/routes` | Market, research, AI, document, auth, Watchlist, Saved Research endpoints |
| `app/services` | Orchestration, provider-result handling, caching, persistence |
| `app/agents` | Market collection, sentiment, research, resolution, recommendations, routing, AI context |
| `app/auth` | Password hashing, token creation/verification, current-user dependency |
| `app/schemas` | Auth/user-resource validation; some public request models live beside routes |
| `app/models`, `app/db` | Domain models, metadata registration, engine, sessions, declarative base |
| `app/llm`, `app/embeddings` | Provider interfaces, factories, implementations |
| `app/documents`, `app/rag` | Extraction, indexes, chunks, retrieval, vector search |

`app/main.py` registers routers and development CORS. Configuration loads `backend/.env` by an explicit path. See [setup](README.md#local-setup) for environment instructions.

## PostgreSQL Persistence

SQLAlchemy uses a synchronous engine with `pool_pre_ping=True`. `get_db()` yields and closes request sessions. The session factory uses `expire_on_commit=False`.

```text
User (users)
  ├── watchlist_items → WatchlistItem (watchlist_items)
  └── saved_research → SavedResearch (saved_research)
```

| Model | Fields and constraints |
|---|---|
| User | Integer ID, unique indexed email, password hash, optional display name, active flag, creation/update timestamps |
| WatchlistItem | Integer ID, user FK, ticker, creation timestamp; unique `(user_id, ticker)` |
| SavedResearch | Integer ID, user FK, ticker, title, portable JSON content, creation timestamp; index on `(user_id, created_at, id)` |

Child FKs use `ON DELETE CASCADE`. Bidirectional relationships use `all, delete-orphan` and `passive_deletes=True`. This is model/database behavior, not an exposed account-deletion feature.

Timestamps use UTC application defaults, timezone-aware columns, and server defaults. Tickers are trimmed and uppercased.

Alembic imports `app.models` to register `Base.metadata`. Migration chain:

```text
d69bcf88934d  users
    ↓
908bb8f1f14b  watchlist_items
    ↓
a73e92c4d601  saved_research
```

Migrations are explicit; startup does not create or upgrade tables.

## Authentication and Ownership

1. Registration normalizes email and stores a pwdlib/Argon2 password hash.
2. JSON login or form-compatible token entry authenticates credentials.
3. PyJWT issues an access token with user ID in `sub` and expiry.
4. `get_current_user()` decodes the token and loads an active user.
5. Protected services receive `current_user.id`; frontend ownership fields are not used.

`GET /api/auth/me` omits the password hash. Invalid/expired credentials or inactive/missing users return 401. `/api/auth/token` accepts email as form `username` for Swagger; it is not social OAuth.

Watchlist operations filter by the current user. Duplicate normalized tickers for one user return 409.

Saved Research detail/deletion filter by both ID and owner. Foreign-owned and nonexistent records return identical 404 responses. Responses omit the ownership column.

## Saved Research Flow

```text
Displayed research_summary → explicit Save → authenticated POST
  → PostgreSQL JSON snapshot → metadata list → full saved detail
```

The create schema accepts ticker, structured content, and optional title. It validates core report text, ticker consistency, section containers, and arrays while preserving additional fields and optional/null values. Missing/blank titles are generated from company name or ticker.

The UI submits the summary with warnings/market metadata, not raw stock/news envelopes, history arrays, chat answers, or document results. Repeated snapshots are permitted; there is no deduplication, regeneration, editing, or versioning.

Lists omit full content and order by creation time then ID descending. Detail uses stored content through `ResearchSummary` without new research calls.

## Public Market and News Flows

### Stock and Company Data

`StockService` normalizes tickers and uses per-instance in-memory caches: metrics for 60 seconds and nonempty history for five minutes. Unusable all-null metrics and empty history are not cached.

`StockDataAgent` combines yfinance fast/info fields and fallback price sources, sanitizes non-finite numbers, and reports degraded-data warnings.

History tries direct Yahoo chart data, then `Ticker.history`, then `yf.download`. Chart requests retry alternate Yahoo hosts. The 1D UI range uses 5-minute candles; 5D/1M/6M use daily candles. Intraday timestamps preserve distinct candles. This is best-effort retrieval, not streaming.

Company profiles use `CompanyService`/`CompanyAgent` with yfinance and identity fallbacks. `TickerResolverAgent` resolves curated aliases and preserves ticker-shaped input without an LLM. Related-company recommendations are deterministic.

### News and Sentiment

`NewsAgent` builds bounded candidates from the query, known company name, and aliases. Each candidate tries NewsAPI when configured, then Yahoo news, returning the first relevant result set.

Relevance checks use titles/descriptions, aliases, and business terms for ambiguous names. Known-company candidates are capped at five. Missing relevant coverage produces a warning rather than fabricated articles.

`NewsService` attaches TextBlob sentiment/polarity, with financial-term rules for near-neutral text.

## Research Summary

`ResearchService` collects metrics, one-month history, and up to five news articles. `ResearchAgent` deterministically produces identity, overall view, confidence, price analysis, news sentiment, valuation, signal/risk/watch lists, summary text, and disclaimer.

The service adds market metadata and warnings. The public response wraps `research_summary` alongside stock/news data. `ResearchSummary.jsx` renders the structured result.

This path does not call an LLM and remains separate from chat generation.

## Chat and Generation Providers

`ChatService` coordinates `ChatAgent`, `LLMAgent`, `RAGService`, and company/stock/news/research/recommendation services.

Modes are `auto`, `llm`, `company`, and `rag`. Routing is deterministic. Company-mode context selection is question-aware and can collect company profile, metrics, history, news, research, and recommendations. Responses include source/context status and warnings.

Generation uses a factory with null, Ollama, and OpenAI-compatible implementations. Ollama can serve the configured `llama3.1:8b` model. Model/base URL selection belongs to configuration, not service logic; an adapter does not imply every hosted provider was tested.

## Documents, Embeddings, and Retrieval

Two entry paths share retrieval primitives:

1. `POST /api/rag/test` and supplied-document chat build request-scoped indexes.
2. Upload extracts/chunks/embeds once, retaining an index in `DocumentIndexStore` for later questions by document ID.

Uploads support UTF-8 TXT/Markdown and text-based PDFs through pypdf. Validation covers type, byte/text limits, page count, and sufficient extracted text. Encrypted PDFs and documents without usable text are rejected. No OCR is implemented.

```text
Upload → extraction → page-aware text units → overlapping chunks
       → embeddings → in-memory cosine-similarity index
Question → query embedding → retrieval → generation
         → answer and source/page metadata
```

Embedding providers are null or Ollama. `nomic-embed-text` is used when configured with enabled Ollama embeddings; the template leaves embeddings disabled.

Uploaded indexes survive requests only within the same backend process and disappear on restart. They are not PostgreSQL-backed, shared across workers, or user-owned. Document endpoints are public.

## Frontend Architecture

| Route | Page |
|---|---|
| `/`, `/stock/:ticker` | Route-aware Dashboard |
| `/login`, `/signup` | Account entry |
| `/watchlist` | Authenticated Watchlist |
| `/saved-research`, `/saved-research/:id` | Authenticated snapshot list/detail |

`AuthContext` restores a localStorage access token through `/api/auth/me`. Logout clears local session/token state. There is no refresh-token or server-side token-revocation workflow.

API modules use Fetch and Bearer headers for private requests. Public GET helpers cache where appropriate. Component-local state and abort/cleanup patterns handle pending and stale requests; no global Saved Research store exists.

`Dashboard` coordinates stock, company, history, news, and research. `AIResearchAssistant` provides chat and document Q&A with sources. `ResearchSummary` renders saved content with Save hidden.

Logged-out Save/Watch clicks use the existing internal login return route. Save requires another explicit click after login. Saved feedback is local to the result/session. Native delete confirmation precedes the request; errors preserve cards except already-unavailable 404 results.

## Current Architectural Limitations

- PostgreSQL covers only users, Watchlists, and Saved Research.
- Provider failures can yield incomplete data; caches/indexes are process-local.
- No persistent document ownership, conversation history, OCR, or automated filing ingestion.
- No refresh tokens, social login, portfolio, or social/discovery backend.
- Frontend automated interaction tests are not configured.
- Development proxy/CORS and local providers are not production infrastructure.

See [README](README.md) for setup and [PROJECT.md](PROJECT.md) for milestones.

