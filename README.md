# AI Stock Intelligence Platform

A full-stack stock research platform that combines market data, company intelligence, AI agents, local LLMs, and RAG-based document Q&A.

The project started as a stock dashboard and has evolved into an AI-powered research assistant for exploring listed companies, understanding business fundamentals, reading market context, and asking questions against uploaded company documents.

## Current Status

The platform currently supports:

* Stock search by ticker and company name
* Real-time stock overview using `yfinance`
* Historical price charts
* Company profile intelligence
* News retrieval with sentiment labels
* Rule-based research summaries
* Related company recommendations
* Backend agent architecture
* Local LLM support through Ollama
* AI Research Assistant on the stock detail page
* RAG over uploaded `.txt` and `.md` documents
* Document-grounded answers with source metadata

This is an active long-term project. The current version focuses on building a clean AI research foundation before adding accounts, portfolios, persistence, and social investing features.

## Tech Stack

### Frontend

* React
* Vite
* React Router
* Recharts
* Native Fetch API

### Backend

* FastAPI
* Python
* yfinance
* NewsAPI
* TextBlob
* Ollama
* In-memory caching
* In-memory vector retrieval for local RAG prototype

### AI and RAG

* Provider-neutral LLM abstraction
* Null LLM provider
* OpenAI-compatible provider
* Ollama chat provider
* Provider-neutral embedding abstraction
* Ollama embedding provider
* Local embedding model: `nomic-embed-text`
* Local chat model: `llama3.1:8b`
* Deterministic chunking
* Cosine similarity retrieval
* Request-scoped and uploaded-document RAG flows

## Features

## Stock Research

Users can search for a company or ticker and view:

* Current stock price and key metrics
* Historical price chart
* Market metadata
* Currency-aware formatting
* Company profile
* Business summary
* News articles
* Sentiment analysis
* Rule-based research summary
* Related companies

The search system supports both exact tickers and company names, for example:

* `Infosys` → `INFY.NS`
* `Reliance` → `RELIANCE.NS`
* `TCS` → `TCS.NS`
* `Apple` → `AAPL`
* `Microsoft` → `MSFT`

## AI Research Assistant

The stock detail page includes an AI Research Assistant that can answer company-focused questions using the selected ticker.

Example questions:

* What does this company do?
* Explain this company simply.
* What are the main business areas?
* What should I know about this company?

The assistant sends the active ticker to the backend and uses company context when available.

## Document Q&A

The assistant also supports document-based Q&A for uploaded text files.

Supported file types:

* `.txt`
* `.md`

Flow:

1. Upload a UTF-8 text or markdown file.
2. Backend extracts text.
3. Text is chunked.
4. Chunks are embedded using Ollama.
5. The document is indexed in process memory.
6. User asks questions against the uploaded document.
7. The answer is generated using retrieved chunks and returned with source metadata.

Current limitations:

* Uploaded documents are stored only in backend process memory.
* Uploaded document indexes are cleared when the backend restarts.
* PDF support is not implemented yet.
* No persistent vector database is used yet.

## Backend Architecture

The backend follows a layered architecture:

```text
API Route
↓
Service
↓
Agent
↓
Provider / External API / Logic
```

Examples:

```text
chat_routes.py
↓
ChatService
↓
ChatAgent / LLMAgent / RAGService
```

```text
rag_routes.py
↓
RAGService
↓
RAGAgent
↓
Embedding Provider + Vector Store
```

```text
search_routes.py
↓
TickerResolverService
↓
TickerResolverAgent
```

This keeps routes thin, services responsible for orchestration, and agents focused on intelligence or retrieval logic.

## Main Backend Agents

Current backend agents include:

* `StockDataAgent`
* `NewsAgent`
* `SentimentAgent`
* `ResearchAgent`
* `CompanyAgent`
* `RecommendationAgent`
* `RouterAgent`
* `LLMAgent`
* `RAGAgent`
* `ChatAgent`
* `TickerResolverAgent`

## Main API Endpoints

### Core

```text
GET  /api/health
GET  /api/stocks/{ticker}
GET  /api/stocks/{ticker}/history
GET  /api/news/{query}
POST /api/sentiment
GET  /api/research/{ticker}
GET  /api/company/{ticker}
GET  /api/recommendations/{ticker}
GET  /api/router/{ticker}?intent=...
```

### Phase 3 AI Endpoints

```text
GET  /api/llm/status
POST /api/llm/test
GET  /api/search/resolve?query=...
POST /api/rag/test
POST /api/chat
POST /api/documents/upload
POST /api/documents/{document_id}/ask
```

## Local Setup

## Backend

The supported backend runtime is Python 3.12.

Go to the backend folder:

```powershell
cd backend
```

Create a Python 3.12 virtual environment, activate it, and install dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

If the Windows Python launcher does not detect installed interpreters, invoke
the Python 3.12 executable by its full path for the `-m venv .venv` command.

Create a `.env` file in the backend folder.

Example local configuration:

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

DOCUMENT_UPLOAD_MAX_BYTES=1048576
DOCUMENT_TEXT_MAX_CHARS=100000
DOCUMENT_INDEX_MAX_DOCUMENTS=25
```

Start Ollama and install the required local models if they are not already
available:

```powershell
ollama serve
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama list
```

Run the backend:

```powershell
python -m uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

## Frontend

Go to the frontend folder:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Run the frontend:

```powershell
npm.cmd run dev
```

Frontend runs at:

```text
http://localhost:5173
```

## Testing

Backend tests:

```powershell
cd backend
python -m unittest discover -s tests -p "test_*.py" -v
python mvp_smoke.py
```

Frontend build:

```powershell
cd frontend
npm.cmd run build
```

Frontend lint:

```powershell
cd frontend
npm.cmd run lint
```

## Current Limitations

The current version is designed for local development and portfolio demonstration.

Known limitations:

* Ollama is used locally for development.
* RAG document indexes are stored in process memory only.
* Uploaded documents disappear after backend restart.
* Only `.txt` and `.md` uploads are supported.
* PDF extraction is not implemented yet.
* No persistent vector database yet.
* No PostgreSQL integration yet.
* No authentication or user accounts yet.
* No saved research history yet.
* Chat is currently single-turn.
* The platform does not provide financial advice.

## Roadmap

Near-term planned improvements:

* PDF extraction with page-aware citations
* Persistent document indexing
* RAG-backed document library
* Richer AI assistant modes using stock, news, research, and filings
* Conversation-style chat UI
* Saved research outputs

Long-term roadmap:

* PostgreSQL database
* User authentication
* Watchlists
* Portfolio tracking
* Saved AI research
* Social investing features
* Community discussions
* Swipe-based stock discovery
* Personalized recommendation engine

## Project Direction

This project is not intended to be a simple stock price prediction app. The goal is to build a practical AI stock research platform that combines market data, company intelligence, AI agents, and document-grounded reasoning into one workflow.

The long-term vision is to evolve it into a social investing and research platform where users can explore companies, ask AI-assisted questions, compare stocks, save research, and eventually interact with a community around investment ideas.
