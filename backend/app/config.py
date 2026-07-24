import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


BACKEND_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(BACKEND_ENV_PATH)


def _get_float(name: str, default: float):
    value = os.getenv(name)

    if value in (None, ""):
        return default

    try:
        return float(value)
    except ValueError:
        return default


def _get_int(name: str, default: int):
    value = os.getenv(name)

    if value in (None, ""):
        return default

    try:
        return int(value)
    except ValueError:
        return default


class Settings(BaseModel):
    app_name: str = "AI Stock Intelligence Platform"
    environment: str = os.getenv("ENVIRONMENT", "development")
    llm_provider: str = os.getenv("LLM_PROVIDER", "none")
    llm_api_key: str | None = os.getenv("LLM_API_KEY")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_base_url: str = os.getenv(
        "LLM_BASE_URL",
        "https://api.openai.com/v1",
    )
    llm_timeout: float = _get_float("LLM_TIMEOUT", 30)
    llm_temperature: float = _get_float("LLM_TEMPERATURE", 0.2)
    llm_max_tokens: int = _get_int("LLM_MAX_TOKENS", 500)
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "none")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    embedding_base_url: str = os.getenv(
        "EMBEDDING_BASE_URL",
        "http://localhost:11434",
    )
    embedding_timeout: float = _get_float("EMBEDDING_TIMEOUT", 60)
    rag_chunk_size: int = _get_int("RAG_CHUNK_SIZE", 1000)
    rag_chunk_overlap: int = _get_int("RAG_CHUNK_OVERLAP", 150)
    rag_retrieval_k: int = _get_int("RAG_RETRIEVAL_K", 5)


settings = Settings()
