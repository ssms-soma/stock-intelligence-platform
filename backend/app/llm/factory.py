from app.config import settings
from app.llm.providers.null_provider import NullLLMProvider
from app.llm.providers.ollama_provider import OllamaProvider
from app.llm.providers.openai_provider import OpenAICompatibleProvider


def create_llm_provider():
    provider = (settings.llm_provider or "none").strip().lower()

    if provider in {"none", "null", "disabled", ""}:
        return NullLLMProvider(model=settings.llm_model)

    if provider == "openai":
        return OpenAICompatibleProvider(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    if provider == "ollama":
        return OllamaProvider(
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

    return NullLLMProvider(model=settings.llm_model)
