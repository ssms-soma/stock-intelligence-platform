# AI Stock Intelligence Platform

## Description

AI Stock Intelligence Platform is a full-stack stock research dashboard that combines market data, historical price charts, company news, sentiment analysis, related companies, and a rule-based research summary into one React frontend backed by a FastAPI API.

The current system focuses on core stock intelligence first. AI reasoning, persistent user features, and social recommendation workflows are planned as future layers.

## Current Tech Stack

- FastAPI backend
- React + Vite frontend
- yfinance for stock metrics and historical price data
- NewsAPI for company and market news
- TextBlob for sentiment analysis
- Recharts for price charts
- React Router for frontend routing

## Completed Features

- Stock metrics lookup
- Stock price history lookup
- Market ticker tape
- Company news
- Sentiment analysis
- Rule-based research summary
- Research frontend section
- Related companies
- Google Finance-style chart periods:
  - 1D
  - 5D
  - 1M
  - 6M
- Frontend route-based stock detail pages
- Loading skeletons for stock detail content
- Fintech-style stock overview, news cards, sentiment badges, related company cards, and research summary cards

## Current Routes

### Frontend Routes

- `/`
  - Market overview landing page.
  - Shows hero section, ticker tape, stock search, and market headlines.

- `/stock/:ticker`
  - Stock detail page for a selected ticker.
  - Shows stock overview, price chart, research summary, related companies, and news.

### Backend API Routes

The backend currently mounts API routers under `/api`.

- `GET /api/health`
- `GET /api/stocks/{ticker}`
- `GET /api/stocks/{ticker}/history`
- `GET /api/news/{query}`
- `POST /api/sentiment`
- `GET /api/research/{ticker}`

## Future Roadmap

The following features are planned and are not part of the completed system unless explicitly implemented later:

- LLM research layer
- Multi-agent orchestration
- PostgreSQL persistence
- Authentication
- User watchlists
- Retrieval-augmented generation (RAG)
- AI chat over stocks, news, and research data
- Social stock discovery
- Swipe-based recommendations
- Production deployment

## Development Philosophy

- Build core stock intelligence first.
- Add AI reasoning second.
- Add user accounts and persistence third.
- Add social recommendation features last.

