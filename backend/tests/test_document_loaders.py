from io import BytesIO
import unittest

from pypdf import PdfWriter
from pypdf.generic import (
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
)

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


def create_pdf(page_texts, encrypted=False):
    output = BytesIO()
    writer = PdfWriter()
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    font_reference = writer._add_object(font)

    for text in page_texts:
        page = writer.add_blank_page(width=612, height=792)
        if text is None:
            continue

        escaped = (
            text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        )
        content = DecodedStreamObject()
        content.set_data(
            f"BT /F1 12 Tf 72 720 Td ({escaped}) Tj ET".encode("latin-1")
        )
        page[NameObject("/Resources")] = DictionaryObject(
            {
                NameObject("/Font"): DictionaryObject(
                    {NameObject("/F1"): font_reference}
                )
            }
        )
        page[NameObject("/Contents")] = writer._add_object(content)

    if encrypted:
        writer.encrypt("secret")

    writer.write(output)
    return output.getvalue()


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
                self.assertEqual(result.units[0].text, "Revenue grew.")
                self.assertIsNone(result.units[0].page)

    async def test_sanitizes_title_with_basename_semantics(self):
        result = await self.loader.load(
            FakeUpload("../private/report.txt", b"Evidence", "text/plain")
        )
        windows_result = await self.loader.load(
            FakeUpload("C:\\private\\notes.md", b"Evidence", "text/markdown")
        )

        self.assertEqual(result.title, "report")
        self.assertEqual(windows_result.title, "notes")

    async def test_extracts_text_pdf_with_one_based_page_numbers(self):
        loader = TextDocumentLoader(
            max_bytes=10_000,
            max_characters=1_000,
            pdf_max_pages=10,
            pdf_min_extracted_characters=10,
        )
        result = await loader.load(
            FakeUpload(
                "../private/annual-report.PDF",
                create_pdf(
                    [
                        "Revenue increased during the year.",
                        None,
                        "Cloud services continued to grow.",
                    ]
                ),
                "application/pdf",
            )
        )

        self.assertEqual(result.title, "annual-report")
        self.assertEqual(result.extension, ".pdf")
        self.assertEqual([unit.page for unit in result.units], [1, 3])
        self.assertIn("Revenue increased", result.units[0].text)

    async def test_accepts_pdf_octet_stream_fallback(self):
        loader = TextDocumentLoader(
            max_bytes=10_000,
            max_characters=1_000,
            pdf_min_extracted_characters=5,
        )

        result = await loader.load(
            FakeUpload(
                "report.pdf",
                create_pdf(["Readable report text."]),
                "application/octet-stream",
            )
        )

        self.assertEqual(result.units[0].page, 1)

    async def test_rejects_extension_and_content_type(self):
        cases = (
            (
                FakeUpload("report.docx", b"text", "application/octet-stream"),
                "Only",
            ),
            (FakeUpload("report.txt", b"text", "image/png"), "content type"),
            (FakeUpload("report.pdf", b"text", "image/png"), "content type"),
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

    async def test_rejects_invalid_blank_and_encrypted_pdfs(self):
        loader = TextDocumentLoader(
            max_bytes=10_000,
            max_characters=1_000,
            pdf_max_pages=10,
            pdf_min_extracted_characters=5,
        )
        cases = (
            (
                FakeUpload("bad.pdf", b"not a pdf", "application/pdf"),
                "invalid",
            ),
            (
                FakeUpload(
                    "blank.pdf",
                    create_pdf([None]),
                    "application/pdf",
                ),
                "Scanned PDFs",
            ),
            (
                FakeUpload(
                    "locked.pdf",
                    create_pdf(["Protected report text."], encrypted=True),
                    "application/pdf",
                ),
                "password-protected",
            ),
        )
        for upload, warning in cases:
            with self.subTest(filename=upload.filename):
                with self.assertRaises(DocumentLoadError) as raised:
                    await loader.load(upload)
                self.assertIn(warning, raised.exception.warning)

    async def test_rejects_pdf_page_and_extracted_character_limits(self):
        page_limited_loader = TextDocumentLoader(
            max_bytes=10_000,
            max_characters=1_000,
            pdf_max_pages=1,
            pdf_min_extracted_characters=1,
        )
        with self.assertRaises(DocumentLoadError) as page_error:
            await page_limited_loader.load(
                FakeUpload(
                    "long.pdf",
                    create_pdf(["First page.", "Second page."]),
                    "application/pdf",
                )
            )
        self.assertEqual(page_error.exception.status_code, 413)
        self.assertIn("page count", page_error.exception.warning)

        character_limited_loader = TextDocumentLoader(
            max_bytes=10_000,
            max_characters=10,
            pdf_max_pages=10,
            pdf_min_extracted_characters=1,
        )
        with self.assertRaises(DocumentLoadError) as character_error:
            await character_limited_loader.load(
                FakeUpload(
                    "verbose.pdf",
                    create_pdf(["This text is longer than ten characters."]),
                    "application/pdf",
                )
            )
        self.assertEqual(character_error.exception.status_code, 413)

    async def test_rejects_pdf_with_too_little_readable_text(self):
        loader = TextDocumentLoader(
            max_bytes=10_000,
            max_characters=1_000,
            pdf_min_extracted_characters=100,
        )

        with self.assertRaises(DocumentLoadError) as raised:
            await loader.load(
                FakeUpload(
                    "short.pdf",
                    create_pdf(["Short text."]),
                    "application/pdf",
                )
            )

        self.assertIn("Scanned PDFs", raised.exception.warning)


if __name__ == "__main__":
    unittest.main()
