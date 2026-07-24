from dataclasses import dataclass, field


@dataclass
class EmbeddingResponse:
    embeddings: list[list[float]]
    provider: str
    model: str | None = None
    model_status: str = "unknown"
    warning: str | None = None
    metadata: dict = field(default_factory=dict)


class BaseEmbeddingProvider:
    provider_name = "base"

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        raise NotImplementedError

    def get_status(self):
        return {
            "provider": self.provider_name,
            "model": None,
            "model_status": "unknown",
            "configured": False,
        }
