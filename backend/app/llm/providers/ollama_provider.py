import requests

from app.llm.base import BaseLLMProvider, LLMRequest, LLMResponse


class OllamaProvider(BaseLLMProvider):
    provider_name = "ollama"

    def __init__(
        self,
        model: str,
        base_url: str,
        timeout: float,
        temperature: float,
        max_tokens: int,
    ):
        self.model = model
        self.base_url = (base_url or "").rstrip("/")
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, request: LLMRequest) -> LLMResponse:
        configuration_warning = self._configuration_warning()
        if configuration_warning:
            return self._unavailable_response(
                configuration_warning,
                model_status="not_configured",
            )

        payload = {
            "model": self.model,
            "messages": self._build_messages(request),
            "stream": False,
            "options": {
                "temperature": (
                    request.temperature
                    if request.temperature is not None
                    else self.temperature
                ),
                "num_predict": (
                    request.max_tokens
                    if request.max_tokens is not None
                    else self.max_tokens
                ),
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
        except requests.Timeout:
            return self._unavailable_response("Ollama request timed out.")
        except requests.ConnectionError:
            return self._unavailable_response(
                "Ollama is unreachable. Make sure the Ollama service is running."
            )
        except requests.RequestException:
            return self._unavailable_response("Ollama request failed.")

        try:
            data = response.json()
        except ValueError:
            return self._unavailable_response(
                "Ollama returned invalid JSON.",
                http_status=response.status_code,
            )

        if not response.ok:
            return self._http_error_response(response.status_code, data)

        try:
            text = data["message"]["content"]
        except (KeyError, TypeError):
            return self._unavailable_response(
                "Ollama returned an unexpected response shape."
            )

        if not isinstance(text, str) or not text.strip():
            return self._unavailable_response("Ollama returned an empty response.")

        return LLMResponse(
            text=text,
            provider=self.provider_name,
            model=data.get("model") or self.model,
            model_status="available",
            metadata={
                "configured": True,
                "done": data.get("done"),
                "done_reason": data.get("done_reason"),
                "prompt_eval_count": data.get("prompt_eval_count"),
                "eval_count": data.get("eval_count"),
            },
        )

    def get_status(self):
        status = {
            "provider": self.provider_name,
            "model": self.model,
            "model_status": "unknown",
            "configured": not bool(self._configuration_warning()),
            "base_url": self.base_url,
            "running": False,
            "available": False,
        }

        configuration_warning = self._configuration_warning()
        if configuration_warning:
            status["model_status"] = "not_configured"
            status["warning"] = configuration_warning
            return status

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=self._status_timeout(),
            )
        except requests.Timeout:
            status["model_status"] = "unavailable"
            status["warning"] = "Ollama status request timed out."
            return status
        except requests.ConnectionError:
            status["model_status"] = "unavailable"
            status["warning"] = (
                "Ollama is unreachable. Make sure the Ollama service is running."
            )
            return status
        except requests.RequestException:
            status["model_status"] = "unavailable"
            status["warning"] = "Ollama status request failed."
            return status

        status["running"] = True

        try:
            data = response.json()
        except ValueError:
            status["model_status"] = "unavailable"
            status["warning"] = "Ollama returned invalid JSON for its model list."
            return status

        if not response.ok:
            status["model_status"] = "unavailable"
            status["warning"] = self._http_warning(response.status_code, data)
            return status

        models = data.get("models")
        if not isinstance(models, list):
            status["model_status"] = "unavailable"
            status["warning"] = "Ollama returned an unexpected model list."
            return status

        model_names = {
            model.get("name")
            for model in models
            if isinstance(model, dict) and isinstance(model.get("name"), str)
        }
        status["available"] = self.model in model_names

        if status["available"]:
            status["model_status"] = "available"
        else:
            status["model_status"] = "not_pulled"
            status["warning"] = (
                f"Ollama is running, but model '{self.model}' is not pulled."
            )

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

    def _configuration_warning(self):
        if not self.model:
            return "LLM_MODEL is not configured for Ollama."
        if not self.base_url:
            return "LLM_BASE_URL is not configured for Ollama."
        return None

    def _status_timeout(self):
        return min(max(self.timeout, 0.1), 5.0)

    def _http_error_response(self, status_code, data):
        warning = self._http_warning(status_code, data)
        model_status = "not_pulled" if status_code == 404 else "unavailable"
        return self._unavailable_response(
            warning,
            model_status=model_status,
            http_status=status_code,
        )

    def _http_warning(self, status_code, data):
        error_message = data.get("error") if isinstance(data, dict) else None

        if status_code == 404:
            detail = error_message or f"model '{self.model}' was not found"
            return f"Ollama model is not available: {detail}"

        if error_message:
            return f"Ollama request failed with HTTP {status_code}: {error_message}"

        return f"Ollama request failed with HTTP {status_code}."

    def _unavailable_response(
        self,
        warning,
        model_status="unavailable",
        http_status=None,
    ):
        metadata = {
            "configured": not bool(self._configuration_warning()),
        }
        if http_status is not None:
            metadata["http_status"] = http_status

        return LLMResponse(
            text="LLM generation is currently unavailable.",
            provider=self.provider_name,
            model=self.model,
            model_status=model_status,
            warning=warning,
            metadata=metadata,
        )
