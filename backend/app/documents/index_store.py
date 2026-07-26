from threading import Lock


class DocumentIndexStoreFullError(RuntimeError):
    pass


class DocumentIndexStore:
    def __init__(self, max_documents: int):
        self.max_documents = max(1, int(max_documents))
        self._documents = {}
        self._lock = Lock()

    def add(self, document):
        with self._lock:
            if (
                document.document_id not in self._documents
                and len(self._documents) >= self.max_documents
            ):
                raise DocumentIndexStoreFullError(
                    "The in-memory document index is full."
                )
            self._documents[document.document_id] = document
        return document

    def get(self, document_id):
        with self._lock:
            return self._documents.get(document_id)

    def has_capacity(self):
        with self._lock:
            return len(self._documents) < self.max_documents

    def __len__(self):
        with self._lock:
            return len(self._documents)
