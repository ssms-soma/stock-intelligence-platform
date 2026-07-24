from app.embeddings.base import BaseEmbeddingProvider, EmbeddingResponse


class NullEmbeddingProvider(BaseEmbeddingProvider):
    provider_name = "null"
    WARNING = "Embedding provider is disabled or not configured."

    def __init__(self, model: str | None = None):
        self.model = model

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        return EmbeddingResponse(
            embeddings=[],
            provider=self.provider_name,
            model=self.model,
            model_status="disabled",
            warning=self.WARNING,
            metadata={
                "configured": False,
                "input_count": len(texts),
            },
        )

    def get_status(self):
        return {
            "provider": self.provider_name,
            "model": self.model,
            "model_status": "disabled",
            "configured": False,
            "warning": self.WARNING,
        }
