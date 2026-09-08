import unittest

from src.rag_core import chunk_text


class TestChunkText(unittest.TestCase):
    def test_short_text_becomes_one_chunk(self):
        # Input smaller than chunk_size -- should come back as exactly one
        # chunk, containing all the text, attributed to page 1.
        pages = [{"page": 1, "text": "This is a short piece of text."}]

        chunks = chunk_text(pages, chunk_size=1200, overlap=300)

        self.assertEqual(len(chunks), 1)
        self.assertIn("short piece of text", chunks[0]["text"])
        self.assertEqual(chunks[0]["pages"], [1, 1])

        

    def test_long_text_splits_with_overlap(self):
        # A page with more text than chunk_size should produce more than
        # one chunk, and consecutive chunks should share some text at the
        # boundary -- that's what "overlap" is supposed to guarantee.
        long_text = "word " * 500  # way more than chunk_size=100 chars
        pages = [{"page": 1, "text": long_text}]

        chunks = chunk_text(pages, chunk_size=100, overlap=30)

        self.assertGreater(len(chunks), 1)

        first_chunk_tail = chunks[0]["text"][-30:]
        second_chunk_head = chunks[1]["text"][:30]
        self.assertTrue(
            any(first_chunk_tail[i:] in chunks[1]["text"] for i in range(len(first_chunk_tail))),
            "expected some overlap between consecutive chunks",
        )


if __name__ == "__main__":
    unittest.main()