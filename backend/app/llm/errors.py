class LLMError(Exception):
    """Base exception for LLM provider failures."""


class LLMConfigurationError(LLMError):
    """Raised when an LLM provider is missing required configuration."""


class LLMProviderError(LLMError):
    """Raised when an LLM provider request fails."""
