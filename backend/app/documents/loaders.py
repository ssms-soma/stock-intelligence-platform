from io import BytesIO
from pathlib import PurePath

from pypdf import PdfReader

from app.documents.models import LoadedDocument, LoadedDocumentUnit


class DocumentLoadError(ValueError):
    def __init__(self, warning: str, status_code: int = 400):
        super().__init__(warning)
        self.warning = warning
        self.status_code = status_code


class TextDocumentLoader:
    ALLOWED_CONTENT_TYPES = {
        ".txt": {"text/plain", "application/octet-stream"},
        ".md": {
            "text/markdown",
            "text/plain",
            "application/octet-stream",
        },
        ".pdf": {"application/pdf", "application/octet-stream"},
    }

    def __init__(
        self,
        max_bytes: int,
        max_characters: int,
        pdf_max_pages: int = 100,
        pdf_min_extracted_characters: int = 100,
    ):
        self.max_bytes = max(1, int(max_bytes))
        self.max_characters = max(1, int(max_characters))
        self.pdf_max_pages = max(1, int(pdf_max_pages))
        self.pdf_min_extracted_characters = max(
            1,
            int(pdf_min_extracted_characters),
        )

    async def load(self, upload_file):
        filename = str(getattr(upload_file, "filename", "") or "").strip()
        if not filename:
            raise DocumentLoadError("A non-empty filename is required.")

        safe_name = PurePath(filename.replace("\\", "/")).name
        extension = PurePath(safe_name).suffix.lower()
        if extension not in self.ALLOWED_CONTENT_TYPES:
            raise DocumentLoadError(
                "Only .txt, .md, and .pdf files are supported."
            )

        content_type = (
            str(getattr(upload_file, "content_type", "") or "")
            .split(";", 1)[0]
            .strip()
            .lower()
        )
        if content_type not in self.ALLOWED_CONTENT_TYPES[extension]:
            raise DocumentLoadError(
                "The uploaded file has an unsupported content type."
            )

        content = await upload_file.read(self.max_bytes + 1)
        if len(content) > self.max_bytes:
            raise DocumentLoadError(
                "The uploaded file exceeds the maximum allowed size.",
                status_code=413,
            )

        title = PurePath(safe_name).stem.strip()
        if not title:
            raise DocumentLoadError("The uploaded file requires a valid title.")

        if extension == ".pdf":
            units = self._extract_pdf_units(content)
        else:
            units = self._extract_text_unit(content)

        return LoadedDocument(
            title=title,
            extension=extension,
            content_type=content_type,
            units=units,
        )

    def _extract_text_unit(self, content):
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as error:
            raise DocumentLoadError(
                "The uploaded file must contain valid UTF-8 text."
            ) from error

        if len(text) > self.max_characters:
            raise DocumentLoadError(
                "The decoded document exceeds the maximum allowed text length.",
                status_code=413,
            )
        if not text.strip():
            raise DocumentLoadError("The uploaded document is empty.")

        return [LoadedDocumentUnit(text=text)]

    def _extract_pdf_units(self, content):
        try:
            reader = PdfReader(BytesIO(content), strict=False)
            if reader.is_encrypted:
                raise DocumentLoadError(
                    "Encrypted or password-protected PDFs are not supported."
                )

            page_count = len(reader.pages)
            if page_count > self.pdf_max_pages:
                raise DocumentLoadError(
                    "The PDF exceeds the maximum allowed page count.",
                    status_code=413,
                )

            units = []
            total_characters = 0
            extracted_characters = 0
            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if not text.strip():
                    continue

                total_characters += len(text)
                if total_characters > self.max_characters:
                    raise DocumentLoadError(
                        "The extracted PDF text exceeds the maximum allowed "
                        "text length.",
                        status_code=413,
                    )

                extracted_characters += sum(
                    1 for character in text if not character.isspace()
                )
                units.append(
                    LoadedDocumentUnit(
                        text=text,
                        page=page_number,
                    )
                )
        except DocumentLoadError:
            raise
        except Exception as error:
            raise DocumentLoadError(
                "The uploaded PDF is invalid or could not be read."
            ) from error

        if (
            not units
            or extracted_characters < self.pdf_min_extracted_characters
        ):
            raise DocumentLoadError(
                "Could not extract readable text from this PDF. Scanned PDFs "
                "are not supported yet."
            )

        return units
