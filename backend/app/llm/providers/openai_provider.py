import requests

from app.llm.base import BaseLLMProvider, LLMRequest, LLMResponse


class OpenAICompatibleProvider(BaseLLMProvider):
    provider_name = "openai"

    def __init__(
        self,
        api_key: str | None,
        model: str,
        base_url: str,
        timeout: float,
        temperature: float,
        max_tokens: int,
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = (base_url or "").rstrip("/")
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, request: LLMRequest) -> LLMResponse:
        if not self.api_key:
            return self._unavailable_response("LLM_API_KEY is not configured.")

        if not self.base_url:
            return self._unavailable_response("LLM_BASE_URL is not configured.")

        payload = {
            "model": self.model,
            "messages": self._build_messages(request),
            "temperature": (
                request.temperature
                if request.temperature is not None
                else self.temperature
            ),
            "max_tokens": (
                request.max_tokens
                if request.max_tokens is not None
                else self.max_tokens
            ),
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
        except requests.Timeout:
            return self._unavailable_response("LLM provider request timed out.")
        except requests.RequestException as error:
            return self._unavailable_response(f"LLM provider request failed: {error}")
        except ValueError:
            return self._unavailable_response("LLM provider returned invalid JSON.")

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            return self._unavailable_response("LLM provider returned an unexpected response shape.")

        return LLMResponse(
            text=text or "",
            provider=self.provider_name,
            model=data.get("model") or self.model,
            model_status="available",
            metadata={
                "configured": True,
                "finish_reason": self._get_finish_reason(data),
                "usage": data.get("usage", {}),
            },
        )

    def get_status(self):
        status = {
            "provider": self.provider_name,
            "model": self.model,
            "model_status": "configured" if self.api_key else "missing_api_key",
            "configured": bool(self.api_key),
            "base_url": self.base_url,
        }

        if not self.api_key:
            status["warning"] = "LLM_API_KEY is not configured."

        return status

    def _build_messages(self, request: LLMRequest):
        messages = []

        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        if request.context:
            messages.append(
                {
                    "role": "system",
                    "content": f"Context:\n{request.context}",
                }
            )

        messages.append({"role": "user", "content": request.prompt})
        return messages

    def _unavailable_response(self, warning):
        return LLMResponse(
            text="LLM generation is currently unavailable.",
            provider=self.provider_name,
            model=self.model,
            model_status="unavailable",
            warning=warning,
            metadata={
                "configured": bool(self.api_key),
            },
        )

    def _get_finish_reason(self, data):
        try:
            return data["choices"][0].get("finish_reason")
        except (KeyError, IndexError, TypeError):
            return None
