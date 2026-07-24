from dataclasses import dataclass, field


@dataclass
class LLMRequest:
    prompt: str
    system_prompt: str | None = None
    context: dict | None = None
    temperature: float | None = None
    max_tokens: int | None = None


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str | None = None
    model_status: str = "unknown"
    warning: str | None = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self):
        response = {
            "response": self.text,
            "provider": self.provider,
            "model": self.model,
            "model_status": self.model_status,
            "metadata": self.metadata,
        }

        if self.warning:
            response["warning"] = self.warning

        return response


class BaseLLMProvider:
    provider_name = "base"

    def generate(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError

    def get_status(self):
        return {
            "provider": self.provider_name,
            "model": None,
            "model_status": "unknown",
            "configured": False,
        }
