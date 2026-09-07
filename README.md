# AI Stock Intelligence Platform

Explore companies, review market context, ask AI-assisted questions, and save research to a personal account.

## Overview

This full-stack research application combines a React dashboard, a FastAPI backend, PostgreSQL user data, deterministic analysis, and optional language-model generation. It is primarily a local-development and portfolio project, not a claim of production deployment or guaranteed real-time market data.

## Current Features

### Public Stock Intelligence

- Search curated company aliases or enter exact tickers, including Indian market symbols such as `INFY.NS`.
- View stock metrics, company profiles, currency-aware prices, market headlines, and related companies.
- Explore 1D, 5D, 1M, and 6M charts. The 1D range uses 5-minute candles; the other supported ranges use daily candles.
- Read news with sentiment labels and structured, rule-based research summaries.

Data is request-based and cached where appropriate. Yahoo Finance chart requests and yfinance provide fallback paths. News uses NewsAPI when configured, Yahoo fallback, and company-alias/relevance filtering.

### Accounts, Watchlists, and Saved Research

- Register and log in with email/password.
- Restore a stored access token through `GET /api/auth/me`.
- Maintain a personal Watchlist with normalized tickers.
- Save a Research Summary, browse saved metadata, open full snapshots, and delete them after confirmation.

Ownership comes from the authenticated user on the server; the frontend does not submit `user_id` for owned resources. Watchlists enforce uniqueness per user/ticker. Saved Research allows repeated snapshots, including identical content.

Saved Research preserves the selected structured summary, warnings, and currency metadata. It does not save the raw stock/news envelope, chat answers, or document results. Opening a snapshot does not regenerate research.

### AI Assistant and Document Q&A

| Workflow | Implementation |
|---|---|
| Research Summary | Deterministic rules combine price movement, sentiment, valuation fields, and signals; no LLM generation. |
| Stock-context chat | Configured generation uses question-aware company, stock, history, news, research, or recommendation context. |
| Document Q&A | Extraction, chunking, embeddings, and retrieval supply context to configured generation. |

Uploads support UTF-8 TXT/Markdown and text-based PDFs. Answers include retrieval source metadata and PDF page references where available. PDF extraction does not perform OCR.

Ollama can provide `llama3.1:8b` generation and `nomic-embed-text` embeddings when the respective providers are enabled. Null providers disable those capabilities. An OpenAI-compatible generation adapter also exists.

## Tech Stack

| Area | Technologies |
|---|---|
| Frontend | React, Vite, React Router, Recharts, CSS, Fetch, AuthContext |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| Persistence | PostgreSQL, SQLAlchemy, psycopg, Alembic |
| Authentication | PyJWT, pwdlib with Argon2 |
| Market/news analysis | Yahoo Finance, yfinance, NewsAPI, TextBlob, financial-term sentiment rules |
| AI/documents | Provider abstractions, Ollama, pypdf, custom chunking and in-memory cosine retrieval |
| Validation | unittest, FastAPI TestClient, SQLite fixtures, ESLint, Vite build |

Canonical dependency versions are in [backend requirements](backend/requirements.txt), [frontend package metadata](frontend/package.json), and the frontend lockfile.

## Architecture

Public intelligence follows `route → service → agent → provider or rules`. Owned data follows `route → auth dependency → service → SQLAlchemy/PostgreSQL`.

```text
User
 ├── WatchlistItem
 └── SavedResearch
```

Uploaded-document indexes and vectors remain in process memory; they are not PostgreSQL-backed or user-owned. See [Architecture](ARCHITECTURE.md).

## Project Structure

```text
backend/
  app/
    api/routes/       HTTP endpoints
    auth/             Password/JWT helpers and current-user dependency
    db/               SQLAlchemy base and sessions
    models/           User, WatchlistItem, SavedResearch
    schemas/          Auth and owned-resource validation
    services/         Orchestration and persistence
    agents/           Market, research, routing, and AI logic
    llm/              Generation providers
    embeddings/       Embedding providers
    documents/        Extraction and in-process indexes
    rag/              Chunking and vector retrieval
  alembic/            Schema migrations
  tests/              Backend tests
frontend/
  src/
    pages/            Dashboard, account, Watchlist, Saved Research
    components/       Stock, research, chat/document, and shared UI
    auth/             AuthContext and token storage
    api/              Fetch helpers and public-data caching
    utils/            Market formatting
docs/                 Documentation index
```

## API Overview

All application routes below use the `/api` prefix. Full schemas are available at [local FastAPI docs](http://127.0.0.1:8000/docs).

| Group | Major endpoints |
|---|---|
| Auth entry; no existing session required | `POST /auth/register`, `POST /auth/login`, `POST /auth/token` |
| Public stock/research | `GET /health`, `GET /search/resolve`, `GET /stocks/{ticker}`, `GET /stocks/{ticker}/history`, `GET /company/{ticker}`, `GET /news/{query}`, `POST /sentiment`, `GET /research/{ticker}`, `GET /recommendations/{ticker}`, `GET /router/{ticker}` |
| Public AI/document | `GET /llm/status`, `POST /llm/test`, `POST /chat`, `POST /rag/test`, `POST /documents/upload`, `POST /documents/{document_id}/ask` |
| Authenticated user data | `GET /auth/me`, `GET/POST /watchlist`, `DELETE /watchlist/{ticker}`, `GET/POST /saved-research`, `GET/DELETE /saved-research/{id}` |

Protected requests use Bearer access tokens. `/auth/token` accepts an OAuth2-compatible form for Swagger, with email supplied as `username`; this is not social OAuth login.

## Local Setup

Local setup follows the repository's current configuration. It has not been verified on a fresh machine.

### Prerequisites

- Python 3.12.
- Node/npm compatible with Vite 8: Node 20.19+ in the 20.x line, or 22.12+.
- A running PostgreSQL server, a database, and an application role.
- Optional Ollama for local generation and embeddings.

Examples use PowerShell. Explicit Python paths avoid requiring environment activation; `npm.cmd` avoids PowerShell blocking `npm.ps1`.

### Backend Environment and Dependencies

From the repository root:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If the Python launcher cannot find Python 3.12, use its installed executable path to create the environment.

Copy the template only if no local environment file exists:

```powershell
if (-not (Test-Path -LiteralPath .env)) {
    Copy-Item -LiteralPath .env.example -Destination .env
}
```

Configure your own values privately in `backend/.env`. Do not commit it or put credentials in frontend code.

- Set `DATABASE_URL` for your database using the SQLAlchemy `postgresql+psycopg` driver.
- Set your own securely generated `JWT_SECRET_KEY`. Algorithm and token lifetime are configurable.
- Configure generation and embedding providers independently.
- `NEWS_API_KEY` is optional because Yahoo fallback exists.

Configuration loads `backend/.env` by an explicit path. The template selects Ollama generation but leaves embeddings disabled. See [the template](backend/.env.example) for names and limits; no full environment copy is needed here.

### PostgreSQL and Migrations

Create a database and application role using your PostgreSQL administration tools. Grant the role permissions to create/use the application tables and configure its connection privately.

From `backend`, apply migrations before using authenticated features:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

Database connection configuration is required during application initialization. Disabling AI does not remove that requirement. Starting Uvicorn does not apply migrations.

### Optional Ollama Setup

Ensure Ollama is running; use `ollama serve` if the local Ollama application is not already managing it. Pull only models needed for the enabled capabilities:

```powershell
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama list
```

For generation, select `LLM_PROVIDER=ollama` with the matching model/base URL. For document indexing, select `EMBEDDING_PROVIDER=ollama` with `nomic-embed-text`. Generation alone does not require the embedding model.

Set the respective provider to `none` to disable it. Document Q&A needs functioning embeddings and generation for grounded answers.

### Frontend

From a new terminal at the repository root:

```powershell
cd frontend
npm.cmd ci
```

## Running the App

From `backend`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

From `frontend`, in another terminal:

```powershell
npm.cmd run dev
```

- Backend: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Frontend: [http://localhost:5173](http://localhost:5173)

Vite proxies `/api` to the backend. Development CORS allows `http://localhost:5173`; use that frontend origin with the current configuration.

## Testing

From `backend`, after configuring the backend environment:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Deterministic tests use controlled/local fixtures, mocks, and dependency overrides. Persistence route tests use SQLite instead of writing test records into the normal PostgreSQL database. Application imports still require database configuration.

From `frontend`:

```powershell
npm.cmd run lint
npm.cmd run build
```

No frontend browser/unit testing framework is configured; interaction checks are manual.

Optional live checks, from `backend`:

```powershell
.\.venv\Scripts\python.exe mvp_smoke.py
```

This script may contact market/news services and configured AI providers. It reports PASS/SKIP/FAIL and is separate from deterministic tests. Read its output: successful process exit alone does not guarantee every check passed.

## Current Limitations

- External providers can fail or return incomplete/delayed data. Prices are not guaranteed real-time.
- Company aliases and related-company recommendations use deterministic rules, not exhaustive discovery or personalized ML.
- PDF extraction is text-based; scanned/image-only and encrypted PDFs are unsupported.
- Uploaded-document indexes live in backend process memory, disappear on restart, and have no persistent user ownership.
- Chat is single-turn with no persisted conversation history.
- Saved Research is a repeatable snapshot, not a versioned report or live market view.
- Access tokens are stored in browser localStorage; refresh tokens and social login are not implemented.
- Frontend automated interaction tests are not configured.
- The system is primarily for local development/portfolio demonstration, not a claim of production scale.

The platform is for research and education, not financial advice.

## Roadmap

Future directions, not delivery commitments:

- Portfolio tracking and preferences/personalization.
- Conversation history.
- Persistent user-owned documents and RAG indexes.
- Richer social/discovery experiences.
- Production/deployment hardening.

## Project Documentation

- [Architecture](ARCHITECTURE.md): flows and storage boundaries.
- [Project evolution](PROJECT.md): milestones and direction.
- [Documentation index](docs/README.md).
- [Backend orientation](backend/README.md).
- [Frontend orientation](frontend/README.md).
