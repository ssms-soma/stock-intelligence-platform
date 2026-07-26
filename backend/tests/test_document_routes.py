import unittest
from unittest.mock import AsyncMock, Mock, patch

from fastapi import HTTPException

from app.api.routes.document_routes import (
    DocumentAskRequest,
    ask_document,
    upload_document,
)
from app.services.document_service import DocumentServiceError


class DocumentRoutesTests(unittest.IsolatedAsyncioTestCase):
    async def test_upload_route_delegates_to_service(self):
        expected = {"status": "indexed", "document_id": "doc-1"}
        upload = object()

        with patch(
            "app.api.routes.document_routes.document_service.upload_document",
            new=AsyncMock(return_value=expected),
        ) as mock_upload:
            result = await upload_document(upload)

        self.assertEqual(result, expected)
        mock_upload.assert_awaited_once_with(upload)

    async def test_upload_route_returns_structured_service_error(self):
        with patch(
            "app.api.routes.document_routes.document_service.upload_document",
            new=AsyncMock(
                side_effect=DocumentServiceError("Index full.", 409)
            ),
        ):
            with self.assertRaises(HTTPException) as raised:
                await upload_document(object())

        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(raised.exception.detail["warning"], "Index full.")

    async def test_ask_route_delegates_and_handles_unknown_document(self):
        request = DocumentAskRequest(question="What changed?", top_k=2)
        expected = {"answer": "Growth", "document_id": "doc-1"}

        with patch(
            "app.api.routes.document_routes.document_service.ask_document",
            return_value=expected,
        ) as mock_ask:
            result = ask_document("doc-1", request)

        self.assertEqual(result, expected)
        mock_ask.assert_called_once_with(
            document_id="doc-1",
            question="What changed?",
            top_k=2,
        )

        with patch(
            "app.api.routes.document_routes.document_service.ask_document",
            new=Mock(side_effect=DocumentServiceError("Not found.", 404)),
        ):
            with self.assertRaises(HTTPException) as raised:
                ask_document("missing", request)
        self.assertEqual(raised.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
