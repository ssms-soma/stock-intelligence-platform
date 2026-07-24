from app.config import settings
from app.embeddings.providers.null_provider import NullEmbeddingProvider
from app.embeddings.providers.ollama_provider import OllamaEmbeddingProvider


def create_embedding_provider():
    provider = (settings.embedding_provider or "none").strip().lower()

    if provider == "ollama":
        return OllamaEmbeddingProvider(
            model=settings.embedding_model,
            base_url=settings.embedding_base_url,
            timeout=settings.embedding_timeout,
        )

    return NullEmbeddingProvider(model=settings.embedding_model)
