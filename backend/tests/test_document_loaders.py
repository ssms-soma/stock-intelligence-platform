import unittest

from app.documents.loaders import DocumentLoadError, TextDocumentLoader


class FakeUpload:
    def __init__(self, filename, content, content_type):
        self.filename = filename
        self.content = content
        self.content_type = content_type
        self.requested_size = None

    async def read(self, size):
        self.requested_size = size
        return self.content[:size]


class TextDocumentLoaderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.loader = TextDocumentLoader(max_bytes=20, max_characters=20)

    async def test_loads_txt_and_markdown(self):
        for filename, content_type in (
            ("report.txt", "text/plain"),
            ("notes.MD", "text/markdown"),
        ):
            with self.subTest(filename=filename):
                result = await self.loader.load(
                    FakeUpload(filename, b"Revenue grew.", content_type)
                )
                self.assertEqual(result.title, filename.rsplit(".", 1)[0])
                self.assertEqual(result.text, "Revenue grew.")

    async def test_sanitizes_title_with_basename_semantics(self):
        result = await self.loader.load(
            FakeUpload("../private/report.txt", b"Evidence", "text/plain")
        )
        windows_result = await self.loader.load(
            FakeUpload("C:\\private\\notes.md", b"Evidence", "text/markdown")
        )

        self.assertEqual(result.title, "report")
        self.assertEqual(windows_result.title, "notes")

    async def test_rejects_extension_and_content_type(self):
        cases = (
            (FakeUpload("report.pdf", b"text", "application/pdf"), "Only"),
            (FakeUpload("report.txt", b"text", "image/png"), "content type"),
        )
        for upload, warning in cases:
            with self.subTest(filename=upload.filename):
                with self.assertRaises(DocumentLoadError) as raised:
                    await self.loader.load(upload)
                self.assertIn(warning, raised.exception.warning)
                self.assertEqual(raised.exception.status_code, 400)

    async def test_rejects_oversized_invalid_utf8_and_empty_files(self):
        cases = (
            (
                FakeUpload("large.txt", b"x" * 21, "text/plain"),
                413,
                "maximum allowed size",
            ),
            (
                FakeUpload("bad.txt", b"\xff", "text/plain"),
                400,
                "UTF-8",
            ),
            (
                FakeUpload("empty.md", b" \n ", "application/octet-stream"),
                400,
                "empty",
            ),
        )
        for upload, status_code, warning in cases:
            with self.subTest(filename=upload.filename):
                with self.assertRaises(DocumentLoadError) as raised:
                    await self.loader.load(upload)
                self.assertEqual(raised.exception.status_code, status_code)
                self.assertIn(warning, raised.exception.warning)


if __name__ == "__main__":
    unittest.main()
