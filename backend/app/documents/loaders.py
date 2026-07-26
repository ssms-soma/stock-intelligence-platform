from pathlib import PurePath

from app.documents.models import LoadedDocument


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
    }

    def __init__(self, max_bytes: int, max_characters: int):
        self.max_bytes = max(1, int(max_bytes))
        self.max_characters = max(1, int(max_characters))

    async def load(self, upload_file):
        filename = str(getattr(upload_file, "filename", "") or "").strip()
        if not filename:
            raise DocumentLoadError("A non-empty filename is required.")

        safe_name = PurePath(filename.replace("\\", "/")).name
        extension = PurePath(safe_name).suffix.lower()
        if extension not in self.ALLOWED_CONTENT_TYPES:
            raise DocumentLoadError("Only .txt and .md files are supported.")

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

        title = PurePath(safe_name).stem.strip()
        if not title:
            raise DocumentLoadError("The uploaded file requires a valid title.")

        return LoadedDocument(
            title=title,
            extension=extension,
            content_type=content_type,
            text=text,
        )
