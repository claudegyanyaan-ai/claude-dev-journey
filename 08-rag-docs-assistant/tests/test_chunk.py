"""Hand-crafted text -> verify chunk/heading/metadata boundaries.

No PDF parsing or OCR involved -- chunk_pages() takes the same plain
{"page", "text"} structure extract.py produces, so these tests build that
structure by hand and check the chunking logic in isolation.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import chunk as chunk_mod  # avoid shadowing the built-in-sounding module name


class TestBasicSplitting(unittest.TestCase):
    def test_two_headings_on_one_page(self):
        pages = [
            {
                "page": 1,
                "text": (
                    "1.1 Introduction\n"
                    "Some intro text.\n"
                    "1.2 Details\n"
                    "More detail text."
                ),
            }
        ]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["section"], "1.1")
        self.assertEqual(chunks[0]["chapter"], "1")
        self.assertEqual(chunks[0]["heading"], "Introduction")
        self.assertEqual(chunks[0]["text"], "Some intro text.")
        self.assertEqual(chunks[0]["pages"], [1, 1])

        self.assertEqual(chunks[1]["section"], "1.2")
        self.assertEqual(chunks[1]["heading"], "Details")
        self.assertEqual(chunks[1]["text"], "More detail text.")

    def test_text_before_first_heading_is_discarded(self):
        pages = [{"page": 1, "text": "Some preamble.\nMore preamble.\n1.1 Intro\nBody."}]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["text"], "Body.")

    def test_no_headings_produces_no_chunks(self):
        pages = [{"page": 1, "text": "Just some prose with no numbered heading."}]
        self.assertEqual(chunk_mod.chunk_pages(pages), [])

    def test_multi_line_body_stays_attached_to_its_heading(self):
        # Equations/tables shouldn't get split off from their paragraph --
        # everything until the next heading is one chunk.
        pages = [
            {
                "page": 1,
                "text": (
                    "1.3.2 Noise Figure\n"
                    "The noise figure quantifies SNR degradation:\n"
                    "NF = 2nsp[1 - (1/G)]\n"
                    "The quantum limit is 3 dB."
                ),
            }
        ]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(len(chunks), 1)
        self.assertIn("NF = 2nsp[1 - (1/G)]", chunks[0]["text"])
        self.assertIn("quantum limit", chunks[0]["text"])


class TestChapterAndPageMetadata(unittest.TestCase):
    def test_chapter_derived_from_multi_level_section(self):
        pages = [{"page": 1, "text": "3.5.2 Parametric Amplifiers\nBody text."}]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(chunks[0]["section"], "3.5.2")
        self.assertEqual(chunks[0]["chapter"], "3")

    def test_page_range_spans_multiple_pages(self):
        pages = [
            {"page": 4, "text": "2.1 Intro\nStart of the section."},
            {"page": 5, "text": "still going on the next page."},
            {"page": 6, "text": "and finishes here.\n2.2 Next Section\nNew body."},
        ]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0]["pages"], [4, 6])
        self.assertEqual(chunks[1]["pages"], [6, 6])
        self.assertIn("Start of the section.", chunks[0]["text"])
        self.assertIn("still going on the next page.", chunks[0]["text"])
        self.assertIn("and finishes here.", chunks[0]["text"])


class TestOcrArtifactTolerance(unittest.TestCase):
    def test_dash_prefixed_heading_is_recognized(self):
        pages = [{"page": 1, "text": "- 1.2 Physics of Optical Amplification\nBody."}]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["section"], "1.2")
        self.assertEqual(chunks[0]["heading"], "Physics of Optical Amplification")

    def test_period_prefixed_heading_is_recognized(self):
        pages = [{"page": 1, "text": ". 2.2 EDFA Physics\nBody."}]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["section"], "2.2")
        self.assertEqual(chunks[0]["heading"], "EDFA Physics")

    def test_missing_leading_chapter_digit_is_recovered_from_context(self):
        pages = [
            {
                "page": 2,
                "text": (
                    "1.2 Physics of Optical Amplification\n"
                    "Some body text.\n"
                    ".2.3 Gain Coefficient\n"
                    "The gain coefficient describes amplification strength."
                ),
            }
        ]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[1]["section"], "1.2.3")
        self.assertEqual(chunks[1]["chapter"], "1")
        self.assertEqual(chunks[1]["heading"], "Gain Coefficient")

    def test_missing_leading_digit_without_prior_chapter_is_ignored(self):
        # No real heading has been seen yet, so there's no chapter number
        # to recover the missing digit from -- the line is treated as
        # ordinary (pre-heading, discarded) text rather than guessed at.
        pages = [{"page": 1, "text": ".2.3 Gain Coefficient\nBody."}]
        self.assertEqual(chunk_mod.chunk_pages(pages), [])


class TestDuplicateHeadingCollapsing(unittest.TestCase):
    def test_immediate_duplicate_heading_is_collapsed(self):
        pages = [
            {
                "page": 8,
                "text": (
                    "2.4 EDFA Performance Characteristics\n"
                    "2.4 EDFA Performance Characteristics\n"
                    "The real body content starts here."
                ),
            }
        ]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["section"], "2.4")
        self.assertEqual(chunks[0]["text"], "The real body content starts here.")

    def test_duplicate_with_ocr_prefix_variant_is_still_collapsed(self):
        pages = [
            {
                "page": 8,
                "text": (
                    "2.4 EDFA Performance Characteristics\n"
                    "- 2.4 EDFA Performance Characteristics\n"
                    "Body content."
                ),
            }
        ]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["text"], "Body content.")

    def test_duplicate_with_repeated_body_line_is_collapsed(self):
        # The real document's Section 6.5.2: heading *and* its opening
        # sentence both duplicated before the real content continues.
        # Should end up as one chunk with the real content, not a tiny
        # "stub" chunk plus a separate real one.
        pages = [
            {
                "page": 36,
                "text": (
                    "6.5.2 Implementation Challenges and Solutions\n"
                    "Real-world implementation faces several challenges that must be addressed:\n"
                    "6.5.2 Implementation Challenges and Solutions\n"
                    "Real-world implementation faces several challenges that must be addressed:\n"
                    "Component Aging: gradual performance degradation."
                ),
            }
        ]
        chunks = chunk_mod.chunk_pages(pages)

        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["section"], "6.5.2")
        self.assertEqual(
            chunks[0]["text"],
            "Real-world implementation faces several challenges that must be addressed:\n"
            "Component Aging: gradual performance degradation.",
        )

    def test_repeat_interrupted_by_a_different_heading_is_not_collapsed(self):
        # Same section number recurring after a *different* heading came
        # between the two occurrences is a genuinely distinct situation --
        # not the immediate back-to-back generation artifact -- so each
        # occurrence keeps its own chunk.
        pages = [
            {
                "page": 1,
                "text": (
                    "1.1 Introduction\n"
                    "First body.\n"
                    "1.2 Something Else\n"
                    "Unrelated body.\n"
                    "1.1 Introduction\n"
                    "Second body."
                ),
            }
        ]
        chunks = chunk_mod.chunk_pages(pages)
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0]["text"], "First body.")
        self.assertEqual(chunks[1]["text"], "Unrelated body.")
        self.assertEqual(chunks[2]["text"], "Second body.")


if __name__ == "__main__":
    unittest.main()
