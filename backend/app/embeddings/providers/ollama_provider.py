import math

import requests

from app.embeddings.base import BaseEmbeddingProvider, EmbeddingResponse


class OllamaEmbeddingProvider(BaseEmbeddingProvider):
    provider_name = "ollama"

    def __init__(self, model: str, base_url: str, timeout: float):
        self.model = model
        self.base_url = (base_url or "").rstrip("/")
        self.timeout = timeout

    def embed(self, texts: list[str]) -> EmbeddingResponse:
        warning = self._configuration_warning()
        if warning:
            return self._unavailable(warning, "not_configured", len(texts))

        if not texts:
            return self._unavailable(
                "No text was provided for embedding.",
                "invalid_input",
                0,
            )

        if any(not isinstance(text, str) or not text.strip() for text in texts):
            return self._unavailable(
                "Embedding input must contain non-empty text values.",
                "invalid_input",
                len(texts),
            )

        try:
            response = requests.post(
                f"{self.base_url}/api/embed",
                json={
                    "model": self.model,
                    "input": texts,
                    "truncate": True,
                },
                timeout=self.timeout,
            )
        except requests.Timeout:
            return self._unavailable(
                "Ollama embedding request timed out.",
                input_count=len(texts),
            )
        except requests.ConnectionError:
            return self._unavailable(
                "Ollama is unreachable. Make sure the Ollama service is running.",
                input_count=len(texts),
            )
        except requests.RequestException:
            return self._unavailable(
                "Ollama embedding request failed.",
                input_count=len(texts),
            )

        try:
            data = response.json()
        except ValueError:
            return self._unavailable(
                "Ollama returned invalid JSON for the embedding request.",
                input_count=len(texts),
                http_status=response.status_code,
            )

        if not response.ok:
            error = data.get("error") if isinstance(data, dict) else None
            if response.status_code == 404:
                detail = error or f"model '{self.model}' was not found"
                warning = f"Ollama embedding model is not available: {detail}"
                model_status = "not_pulled"
            else:
                detail = f": {error}" if error else "."
                warning = (
                    f"Ollama embedding request failed with HTTP "
                    f"{response.status_code}{detail}"
                )
                model_status = "unavailable"

            return self._unavailable(
                warning,
                model_status,
                len(texts),
                response.status_code,
            )

        embeddings = data.get("embeddings") if isinstance(data, dict) else None
        validation_warning = self._validate_embeddings(embeddings, len(texts))
        if validation_warning:
            return self._unavailable(
                validation_warning,
                input_count=len(texts),
            )

        normalized_embeddings = [
            [float(value) for value in vector] for vector in embeddings
        ]
        return EmbeddingResponse(
            embeddings=normalized_embeddings,
            provider=self.provider_name,
            model=data.get("model") or self.model,
            model_status="available",
            metadata={
                "configured": True,
                "input_count": len(texts),
                "dimensions": len(normalized_embeddings[0]),
                "prompt_eval_count": data.get("prompt_eval_count"),
            },
        )

    def get_status(self):
        warning = self._configuration_warning()
        status = {
            "provider": self.provider_name,
            "model": self.model,
            "model_status": "configured" if not warning else "not_configured",
            "configured": not bool(warning),
            "base_url": self.base_url,
        }
        if warning:
            status["warning"] = warning
        return status

    def _validate_embeddings(self, embeddings, expected_count):
        if not isinstance(embeddings, list):
            return "Ollama returned an unexpected embedding response shape."

        if len(embeddings) != expected_count:
            return "Ollama returned a different number of embeddings than requested."

        expected_dimensions = None
        for vector in embeddings:
            if not isinstance(vector, list) or not vector:
                return "Ollama returned an empty or malformed embedding vector."

            if expected_dimensions is None:
                expected_dimensions = len(vector)
            elif len(vector) != expected_dimensions:
                return "Ollama returned embedding vectors with inconsistent dimensions."

            for value in vector:
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                ):
                    return "Ollama returned a non-numeric embedding value."

        return None

    def _configuration_warning(self):
        if not self.model:
            return "EMBEDDING_MODEL is not configured for Ollama."
        if not self.base_url:
            return "EMBEDDING_BASE_URL is not configured for Ollama."
        return None

    def _unavailable(
        self,
        warning,
        model_status="unavailable",
        input_count=0,
        http_status=None,
    ):
        metadata = {
            "configured": not bool(self._configuration_warning()),
            "input_count": input_count,
        }
        if http_status is not None:
            metadata["http_status"] = http_status

        return EmbeddingResponse(
            embeddings=[],
            provider=self.provider_name,
            model=self.model,
            model_status=model_status,
            warning=warning,
            metadata=metadata,
        )
