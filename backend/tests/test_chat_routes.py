import unittest
from unittest.mock import patch

from app.api.routes.chat_routes import ChatDocumentRequest, ChatRequest, chat


class ChatRoutesTests(unittest.TestCase):
    def test_route_delegates_to_chat_service(self):
        request = ChatRequest(
            message="What does Infosys provide?",
            ticker="INFY.NS",
            mode="rag",
            documents=[
                ChatDocumentRequest(
                    document_id="doc-1",
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
            "mode": "rag",
            "ticker": "INFY.NS",
            "sources": [],
            "metadata": {},
            "warning": None,
        }

        with patch(
            "app.api.routes.chat_routes.chat_service.chat",
            return_value=expected,
        ) as mock_chat:
            result = chat(request)

        self.assertEqual(result, expected)
        call = mock_chat.call_args.kwargs
        self.assertEqual(call["message"], request.message)
        self.assertEqual(call["ticker"], "INFY.NS")
        self.assertEqual(call["mode"], "rag")
        self.assertEqual(call["documents"][0]["document_id"], "doc-1")
        self.assertEqual(call["top_k"], 2)


if __name__ == "__main__":
    unittest.main()
