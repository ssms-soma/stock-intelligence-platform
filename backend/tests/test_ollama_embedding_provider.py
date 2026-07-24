import unittest
from unittest.mock import Mock, patch

import requests

from app.embeddings.providers.ollama_provider import OllamaEmbeddingProvider


class OllamaEmbeddingProviderTests(unittest.TestCase):
    def setUp(self):
        self.provider = OllamaEmbeddingProvider(
            model="nomic-embed-text",
            base_url="http://localhost:11434",
            timeout=60,
        )

    @patch("app.embeddings.providers.ollama_provider.requests.post")
    def test_embeds_batch_with_native_api(self, mock_post):
        mock_post.return_value = self._response(
            200,
            {
                "model": "nomic-embed-text",
                "embeddings": [[1, 0.5], [0.25, 1]],
                "prompt_eval_count": 4,
            },
        )

        result = self.provider.embed(["first", "second"])

        self.assertEqual(result.embeddings, [[1.0, 0.5], [0.25, 1.0]])
        self.assertEqual(result.model_status, "available")
        self.assertEqual(result.metadata["dimensions"], 2)
        self.assertEqual(
            mock_post.call_args.args[0],
            "http://localhost:11434/api/embed",
        )
        self.assertEqual(
            mock_post.call_args.kwargs["json"],
            {
                "model": "nomic-embed-text",
                "input": ["first", "second"],
                "truncate": True,
            },
        )

    @patch("app.embeddings.providers.ollama_provider.requests.post")
    def test_handles_timeout_and_connection_error(self, mock_post):
        mock_post.side_effect = requests.Timeout()
        timeout_result = self.provider.embed(["text"])
        self.assertIn("timed out", timeout_result.warning)

        mock_post.side_effect = requests.ConnectionError()
        connection_result = self.provider.embed(["text"])
        self.assertIn("unreachable", connection_result.warning)

    @patch("app.embeddings.providers.ollama_provider.requests.post")
    def test_handles_missing_model_and_invalid_json(self, mock_post):
        mock_post.return_value = self._response(
            404,
            {"error": "model not found"},
        )
        missing_result = self.provider.embed(["text"])
        self.assertEqual(missing_result.model_status, "not_pulled")
        self.assertEqual(missing_result.metadata["http_status"], 404)

        invalid_json = Mock(status_code=200, ok=True)
        invalid_json.json.side_effect = ValueError()
        mock_post.return_value = invalid_json
        invalid_result = self.provider.embed(["text"])
        self.assertIn("invalid JSON", invalid_result.warning)

    @patch("app.embeddings.providers.ollama_provider.requests.post")
    def test_validates_count_values_and_dimensions(self, mock_post):
        invalid_cases = (
            ({"embeddings": []}, "different number"),
            ({"embeddings": [[]]}, "empty or malformed"),
            ({"embeddings": [[1, "bad"]]}, "non-numeric"),
            ({"embeddings": [[1, 2], [1]]}, "inconsistent dimensions"),
        )

        for data, warning_text in invalid_cases:
            with self.subTest(data=data):
                texts = ["one", "two"] if len(data["embeddings"]) == 2 else ["one"]
                mock_post.return_value = self._response(200, data)
                result = self.provider.embed(texts)
                self.assertIn(warning_text, result.warning)
                self.assertEqual(result.embeddings, [])

    def test_rejects_empty_input_without_http_call(self):
        result = self.provider.embed([])

        self.assertEqual(result.model_status, "invalid_input")
        self.assertIn("No text", result.warning)

    @staticmethod
    def _response(status_code, data):
        response = Mock(status_code=status_code, ok=200 <= status_code < 300)
        response.json.return_value = data
        return response


if __name__ == "__main__":
    unittest.main()
