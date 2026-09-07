# Frontend

React/Vite renders public stock intelligence, the chat/document assistant, and authenticated Watchlist/Saved Research workflows.

## Structure

- `src/pages`: Dashboard, Login, Signup, Watchlist, SavedResearch, SavedResearchDetail.
- `src/components`: stock cards/charts, ResearchSummary, AIResearchAssistant, navigation, save/watch controls.
- `src/auth`: AuthContext, session restoration, localStorage token helpers.
- `src/api`: Fetch helpers, authenticated headers, public-data caching.
- `src/utils`: market/currency formatting.
- `src/index.css`: shared and feature-specific styles.

React Router serves `/` and `/stock/:ticker` publicly, account entry at `/login` and `/signup`, and protected pages at `/watchlist`, `/saved-research`, and `/saved-research/:id`.

AuthContext restores sessions through `/api/auth/me`. Private calls send Bearer tokens; ownership is derived by the backend, not supplied by the UI.

## Development Commands

After [root setup](../README.md#local-setup), run from this directory:

```powershell
npm.cmd ci
npm.cmd run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api` to `http://127.0.0.1:8000`; run the backend separately. Keep credentials in the backend environment.

## Validation

```powershell
npm.cmd run lint
npm.cmd run build
```

No frontend browser/unit testing framework is configured. Manual checks cover navigation, auth redirects, save/delete states, document interactions, and responsive layouts.

See [architecture](../ARCHITECTURE.md#frontend-architecture) for data-flow boundaries.
