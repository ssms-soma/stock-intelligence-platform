from app.llm.base import BaseLLMProvider, LLMRequest, LLMResponse


class NullLLMProvider(BaseLLMProvider):
    provider_name = "null"

    WARNING = "LLM provider is disabled or not configured."

    def __init__(self, model: str | None = None):
        self.model = model

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text="LLM generation is disabled because no provider is configured.",
            provider=self.provider_name,
            model=self.model,
            model_status="disabled",
            warning=self.WARNING,
            metadata={
                "configured": False,
                "context_included": bool(request.context),
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
