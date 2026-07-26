import unittest

from app.rag.chunker import TextChunker
from app.rag.models import RAGDocument


class TextChunkerTests(unittest.TestCase):
    def test_chunks_deterministically_with_overlap_and_metadata(self):
        document = RAGDocument(
            document_id="doc-1",
            title="Sample",
            source_type="sample_text",
            text="abcdefghijklmnopqrstuvwxyz",
            page=3,
            metadata={"ticker": "TEST"},
        )
        chunker = TextChunker(chunk_size=10, chunk_overlap=3)

        chunks = chunker.chunk_document(document)

        self.assertEqual(
            [chunk.text for chunk in chunks],
            ["abcdefghij", "hijklmnopq", "opqrstuvwx", "vwxyz"],
        )
        self.assertEqual(chunks[0].chunk_id, "doc-1:chunk:0")
        self.assertEqual(chunks[0].page, 3)
        self.assertEqual(chunks[0].metadata, {"ticker": "TEST"})

    def test_normalizes_whitespace_and_skips_blank_documents(self):
        chunker = TextChunker(chunk_size=100, chunk_overlap=10)
        populated = RAGDocument("one", "One", "sample", "hello\n  world")
        blank = RAGDocument("two", "Two", "sample", "   ")

        self.assertEqual(chunker.chunk_document(populated)[0].text, "hello world")
        self.assertEqual(chunker.chunk_document(blank), [])

    def test_invalid_overlap_is_safely_bounded(self):
        chunker = TextChunker(chunk_size=4, chunk_overlap=10)

        self.assertEqual(chunker.chunk_size, 4)
        self.assertEqual(chunker.chunk_overlap, 3)

    def test_page_aware_chunk_ids_are_unique(self):
        chunker = TextChunker(chunk_size=100, chunk_overlap=0)
        documents = [
            RAGDocument("doc-1", "Report", "uploaded_pdf", "Page one", page=1),
            RAGDocument("doc-1", "Report", "uploaded_pdf", "Page two", page=2),
        ]

        chunks = chunker.chunk_documents(documents)

        self.assertEqual(
            [chunk.chunk_id for chunk in chunks],
            ["doc-1:page:1:chunk:0", "doc-1:page:2:chunk:0"],
        )
        self.assertEqual([chunk.page for chunk in chunks], [1, 2])


if __name__ == "__main__":
    unittest.main()
