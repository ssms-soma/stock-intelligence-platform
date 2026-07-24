import unittest
from unittest.mock import patch

from app.api.routes.rag_routes import RAGDocumentRequest, RAGTestRequest, test_rag


class RAGRoutesTests(unittest.TestCase):
    def test_route_delegates_to_rag_service(self):
        request = RAGTestRequest(
            query="What does Infosys do?",
            documents=[
                RAGDocumentRequest(
                    document_id="infosys",
                    title="Infosys overview",
                    source_type="sample_text",
                    text="Infosys provides consulting services.",
                    page=1,
                )
            ],
            top_k=2,
        )
        expected = {
            "answer": "Answer",
            "query": request.query,
            "sources": [],
            "metadata": {"mode": "rag_test"},
            "warning": None,
        }

        with patch(
            "app.api.routes.rag_routes.rag_service.test_rag",
            return_value=expected,
        ) as mock_test_rag:
            result = test_rag(request)

        self.assertEqual(result, expected)
        call = mock_test_rag.call_args.kwargs
        self.assertEqual(call["query"], "What does Infosys do?")
        self.assertEqual(call["documents"][0]["document_id"], "infosys")
        self.assertEqual(call["top_k"], 2)


if __name__ == "__main__":
    unittest.main()
