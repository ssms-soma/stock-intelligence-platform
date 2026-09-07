# Backend

FastAPI provides public stock/research and AI/document endpoints alongside authenticated PostgreSQL Watchlist and Saved Research persistence.

Complete [local setup](../README.md#local-setup) first: Python 3.12 dependencies, private environment configuration, PostgreSQL, and migrations. Optional AI setup is described there.

## Important Folders

- `app/api/routes`: HTTP endpoints.
- `app/services`, `app/agents`: orchestration and intelligence logic.
- `app/auth`: password/JWT helpers and current-user dependency.
- `app/db`, `app/models`, `app/schemas`: sessions, persisted domain, validation.
- `app/llm`, `app/embeddings`: configurable providers.
- `app/documents`, `app/rag`: extraction and in-process retrieval.
- `alembic`: migrations.
- `tests`: deterministic tests and controlled fixtures.

## Run and Test

From this directory:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

See [testing](../README.md#testing) for fixture requirements and separate optional live checks. See [architecture](../ARCHITECTURE.md) for ownership/storage boundaries.
