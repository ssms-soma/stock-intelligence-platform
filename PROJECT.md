# Project Evolution and Direction

## Motivation

AI Stock Intelligence Platform began as a stock dashboard and evolved into a research workspace: explore a company, inspect market context, ask questions, and preserve useful research.

The project demonstrates full-stack engineering through external-data reliability, deterministic analysis, configurable AI, authenticated ownership, relational persistence, and usable frontend flows. It is educational research tooling, not a stock-price prediction engine or financial advice.

## Completed Milestones

| Milestone | Result |
|---|---|
| Public stock intelligence | Metrics, profiles, charts, news/sentiment, related companies, structured rule-based research |
| Layered backend | Thin routes, coordinating services, specialized agents, provider boundaries |
| Phase 3 AI foundation | Generation/embedding abstractions, Ollama, deterministic company resolution, request-scoped RAG, single-turn chat |
| Document research | TXT/Markdown/text-based PDF upload, extraction, retrieval, source/page metadata |
| Grounded chat and reliability | Question-aware context, Yahoo/yfinance fallbacks, meaningful-data caching, news alias/relevance improvements |
| PostgreSQL foundation | SQLAlchemy models/sessions and Alembic migrations |
| Backend authentication | Password hashing, JWT, registration/login, current-user lookup |
| Frontend authentication | Login/signup, AuthContext, token restoration, protected pages |
| Watchlists | User-owned persisted tickers with per-user uniqueness |
| Saved Research | Repeatable structured snapshots, lists/details, ownership checks, deletion |
| Saved Research polish | Delete confirmation, empty-state guidance, local timestamps, saved feedback, responsive styling |

These are completed implementation milestones, not production-deployment claims. Git history records the individual changes.

## Current Product State

Public visitors can research stocks and use configured AI/document capabilities. Authenticated users maintain Watchlists and save research summaries in PostgreSQL.

Research Summary is rule-based. Chat uses configured generation; document Q&A uses retrieval plus generation. Uploaded indexes remain in memory without user ownership, and chat has no persisted history.

Saved Research preserves selected content rather than a live or versioned analysis. Multiple snapshots for one company are supported.

## Development Philosophy

- Build useful stock intelligence before expanding product scope.
- Keep deterministic analysis separate from optional generation.
- Derive owned-resource identity from server authentication.
- Extend established patterns in small, reviewable changes.
- Validate with controlled backend tests and frontend lint/build checks.
- Add social/recommendation features after core research workflows are dependable.

## Future Directions

Directions to evaluate, not delivery promises:

- Portfolio tracking.
- Preferences/personalization.
- Conversation history.
- Persistent user-owned documents and RAG indexes.
- Richer social/discovery experiences, communities, and discussions.
- Production/deployment hardening and broader frontend interaction testing.

Accounts, PostgreSQL, Watchlists, Saved Research, and PDF text extraction are already implemented.

## Further Reading

- [README](README.md): features, setup, running, testing.
- [Architecture](ARCHITECTURE.md): flows and storage boundaries.
- [Documentation index](docs/README.md).

