r"""Fault-tolerant smoke checks for the existing local MVP.

Run from the backend directory with:
    .\.venv\Scripts\python.exe mvp_smoke.py
"""

from pathlib import Path

from fastapi.testclient import TestClient

from app.embeddings.factory import create_embedding_provider
from app.main import app


client = TestClient(app)
SAMPLE_REPORT = Path(__file__).with_name("sample-report.txt")


def report(name, status, detail):
    print(f"[{status}] {name}: {detail}")


def check(name, operation):
    try:
        operation()
    except Exception as error:
        report(name, "FAIL", f"{type(error).__name__}: {error}")


def require_ok(response, name):
    if not response.is_success:
        raise RuntimeError(f"{name} returned HTTP {response.status_code}")
    return response.json()


def health_check():
    data = require_ok(client.get("/api/health"), "health")
    status = "PASS" if data.get("status") == "success" else "FAIL"
    report("backend health", status, data.get("message") or "unexpected response")


def ticker_check():
    data = require_ok(
        client.get("/api/search/resolve", params={"query": "Apple"}),
        "ticker resolution",
    )
    passed = data.get("resolved") is True and data.get("ticker") == "AAPL"
    report("ticker resolution", "PASS" if passed else "FAIL", str(data))


def stock_check():
    data = require_ok(client.get("/api/stocks/AAPL"), "stock endpoint")
    market_fields = (
        "current_price",
        "previous_close",
        "market_cap",
        "volume",
    )
    usable = any(data.get(field) is not None for field in market_fields)
    detail = data.get("warning") or "usable AAPL market data returned"
    report("stock endpoint", "PASS" if usable else "SKIP", detail)


def news_check():
    data = require_ok(
        client.get("/api/news/AAPL", params={"page_size": 3}),
        "news endpoint",
    )
    count = len(data) if isinstance(data, list) else 0
    report(
        "news endpoint",
        "PASS" if count else "SKIP",
        f"{count} article(s) returned",
    )


def ollama_status_check():
    data = require_ok(client.get("/api/llm/status"), "Ollama status")
    available = data.get("available") is True
    report(
        "Ollama status",
        "PASS" if available else "SKIP",
        data.get("warning") or f"model {data.get('model')} is available",
    )


def ollama_generation_check():
    data = require_ok(
        client.post(
            "/api/llm/test",
            json={"prompt": "Reply with exactly: MVP smoke OK"},
        ),
        "Ollama generation",
    )
    generated = bool(data.get("response")) and not data.get("warning")
    report(
        "Ollama generation",
        "PASS" if generated else "SKIP",
        data.get("warning") or f"model {data.get('model')} generated a response",
    )


def embedding_check():
    response = create_embedding_provider().embed(
        ["Apple designs consumer technology products."],
    )
    available = bool(response.embeddings) and not response.warning
    dimensions = len(response.embeddings[0]) if response.embeddings else 0
    report(
        "embedding generation",
        "PASS" if available else "SKIP",
        response.warning or f"model {response.model}, {dimensions} dimensions",
    )


def document_rag_check():
    if not SAMPLE_REPORT.is_file():
        report("document upload and RAG", "SKIP", "sample-report.txt is missing")
        return

    with SAMPLE_REPORT.open("rb") as sample_file:
        upload = client.post(
            "/api/documents/upload",
            files={"file": (SAMPLE_REPORT.name, sample_file, "text/plain")},
        )
    upload_data = require_ok(upload, "document upload")
    if upload_data.get("status") != "indexed":
        report(
            "document upload and RAG",
            "SKIP",
            upload_data.get("warning") or "document was not indexed",
        )
        return

    document_id = upload_data["document_id"]
    answer = client.post(
        f"/api/documents/{document_id}/ask",
        json={
            "question": "What grew, and what does management expect?",
            "top_k": 5,
        },
    )
    answer_data = require_ok(answer, "document question")
    passed = bool(answer_data.get("answer")) and bool(answer_data.get("sources"))
    detail = answer_data.get("warning") or (
        f"{upload_data.get('chunks_indexed')} chunk(s) indexed; "
        f"{len(answer_data.get('sources') or [])} citation(s) returned"
    )
    report("document upload and RAG", "PASS" if passed else "FAIL", detail)


def main():
    checks = (
        ("backend health", health_check),
        ("ticker resolution", ticker_check),
        ("stock endpoint", stock_check),
        ("news endpoint", news_check),
        ("Ollama status", ollama_status_check),
        ("Ollama generation", ollama_generation_check),
        ("embedding generation", embedding_check),
        ("document upload and RAG", document_rag_check),
    )
    for name, operation in checks:
        check(name, operation)


if __name__ == "__main__":
    main()
