import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.llm.factory import create_llm_provider
from app.llm.providers.null_provider import NullLLMProvider
from app.llm.providers.ollama_provider import OllamaProvider
from app.llm.providers.openai_provider import OpenAICompatibleProvider


class LLMFactoryTests(unittest.TestCase):
    def setUp(self):
        self.settings = SimpleNamespace(
            llm_provider="none",
            llm_api_key=None,
            llm_model="test-model",
            llm_base_url="http://localhost:11434",
            llm_timeout=60,
            llm_temperature=0.3,
            llm_max_tokens=700,
        )

    def test_selects_ollama_provider(self):
        self.settings.llm_provider = "ollama"

        with patch("app.llm.factory.settings", self.settings):
            provider = create_llm_provider()

        self.assertIsInstance(provider, OllamaProvider)
        self.assertEqual(provider.model, "test-model")

    def test_preserves_openai_provider_selection(self):
        self.settings.llm_provider = "openai"
        self.settings.llm_api_key = "test-key"

        with patch("app.llm.factory.settings", self.settings):
            provider = create_llm_provider()

        self.assertIsInstance(provider, OpenAICompatibleProvider)

    def test_null_and_unknown_values_fall_back_safely(self):
        for provider_name in ("none", "null", "disabled", "", "unknown"):
            with self.subTest(provider=provider_name):
                self.settings.llm_provider = provider_name
                with patch("app.llm.factory.settings", self.settings):
                    provider = create_llm_provider()
                self.assertIsInstance(provider, NullLLMProvider)


if __name__ == "__main__":
    unittest.main()
