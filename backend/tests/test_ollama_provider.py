import unittest
from unittest.mock import Mock, patch

import requests

from app.llm.base import LLMRequest
from app.llm.providers.ollama_provider import OllamaProvider


class OllamaProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = OllamaProvider(
            model="llama3.1:8b",
            base_url="http://localhost:11434",
            timeout=60,
            temperature=0.3,
            max_tokens=700,
        )

    @patch("app.llm.providers.ollama_provider.requests.post")
    def test_generate_uses_native_chat_payload(self, mock_post):
        mock_post.return_value = self._response(
            200,
            {
                "model": "llama3.1:8b",
                "message": {"role": "assistant", "content": "Test response"},
                "done": True,
            },
        )

        result = self.provider.generate(
            LLMRequest(
                prompt="Test prompt",
                system_prompt="Test system prompt",
                context={"symbol": "TEST"},
            )
        )

        self.assertEqual(result.text, "Test response")
        self.assertEqual(result.provider, "ollama")
        self.assertEqual(result.model_status, "available")
        payload = mock_post.call_args.kwargs["json"]
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["options"]["temperature"], 0.3)
        self.assertEqual(payload["options"]["num_predict"], 700)
        self.assertEqual(mock_post.call_args.args[0], "http://localhost:11434/api/chat")

    @patch("app.llm.providers.ollama_provider.requests.post")
    def test_generate_handles_unreachable_ollama(self, mock_post):
        mock_post.side_effect = requests.ConnectionError()

        result = self.provider.generate(LLMRequest(prompt="Test"))

        self.assertEqual(result.model_status, "unavailable")
        self.assertIn("unreachable", result.warning)

    @patch("app.llm.providers.ollama_provider.requests.post")
    def test_generate_handles_timeout(self, mock_post):
        mock_post.side_effect = requests.Timeout()

        result = self.provider.generate(LLMRequest(prompt="Test"))

        self.assertEqual(result.model_status, "unavailable")
        self.assertIn("timed out", result.warning)

    @patch("app.llm.providers.ollama_provider.requests.post")
    def test_generate_handles_missing_model(self, mock_post):
        mock_post.return_value = self._response(
            404,
            {"error": "model 'llama3.1:8b' not found"},
        )

        result = self.provider.generate(LLMRequest(prompt="Test"))

        self.assertEqual(result.model_status, "not_pulled")
        self.assertIn("not available", result.warning)
        self.assertEqual(result.metadata["http_status"], 404)

    @patch("app.llm.providers.ollama_provider.requests.post")
    def test_generate_handles_bad_json_and_empty_content(self, mock_post):
        bad_json_response = Mock(status_code=200, ok=True)
        bad_json_response.json.side_effect = ValueError()
        mock_post.return_value = bad_json_response

        bad_json_result = self.provider.generate(LLMRequest(prompt="Test"))
        self.assertIn("invalid JSON", bad_json_result.warning)

        mock_post.return_value = self._response(
            200,
            {"message": {"content": "  "}},
        )
        empty_result = self.provider.generate(LLMRequest(prompt="Test"))
        self.assertIn("empty response", empty_result.warning)

    @patch("app.llm.providers.ollama_provider.requests.get")
    def test_status_reports_pulled_and_missing_models(self, mock_get):
        mock_get.return_value = self._response(
            200,
            {"models": [{"name": "llama3.1:8b"}]},
        )

        available = self.provider.get_status()
        self.assertTrue(available["running"])
        self.assertTrue(available["available"])
        self.assertEqual(available["model_status"], "available")
        self.assertEqual(mock_get.call_args.kwargs["timeout"], 5.0)

        mock_get.return_value = self._response(200, {"models": []})
        missing = self.provider.get_status()
        self.assertTrue(missing["running"])
        self.assertFalse(missing["available"])
        self.assertEqual(missing["model_status"], "not_pulled")

    @staticmethod
    def _response(status_code, data):
        response = Mock(status_code=status_code, ok=200 <= status_code < 300)
        response.json.return_value = data
        return response


if __name__ == "__main__":
    unittest.main()
