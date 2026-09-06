"""Hand-crafted raw-response text -> verify parse_response()'s contract.

No network or API call involved -- same "test pure logic in isolation"
approach as Project 6's formatters and Project 8's chunk.py tests.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import extract  # noqa: E402


class TestParseResponse(unittest.TestCase):
    def test_plain_json_object(self):
        raw = (
            '{"name": "Priya Sharma", "age": "28", '
            '"course_name": "Advanced Python", "contact": "98765-43210", '
            '"email": "priya@example.com"}'
        )
        result = extract.parse_response(raw)
        self.assertEqual(result["name"], "Priya Sharma")
        self.assertEqual(result["age"], "28")

    def test_strips_markdown_code_fence(self):
        # Observed on 2 of 3 real sample emails during manual verification --
        # haiku doesn't always honor "no markdown code fences" in the prompt.
        raw = (
            "```json\n"
            '{"name": "Rohan Mehta", "age": "", "course_name": "Digital Marketing", '
            '"contact": "9876543211", "email": "rohan.mehta@yahoo.com"}\n'
            "```"
        )
        result = extract.parse_response(raw)
        self.assertIsNotNone(result)
        self.assertEqual(result["age"], "")
        self.assertEqual(result["name"], "Rohan Mehta")

    def test_strips_fence_without_json_language_tag(self):
        raw = '```\n{"name": "A", "age": "", "course_name": "", "contact": "", "email": ""}\n```'
        result = extract.parse_response(raw)
        self.assertIsNotNone(result)

    def test_missing_field_becomes_empty_string_not_a_guess(self):
        raw = '{"name": "Rohan Mehta", "course_name": "Digital Marketing"}'
        result = extract.parse_response(raw)
        self.assertEqual(result["age"], "")
        self.assertEqual(result["contact"], "")
        self.assertEqual(result["email"], "")

    def test_invalid_json_returns_none(self):
        result = extract.parse_response("not json at all")
        self.assertIsNone(result)

    def test_non_object_json_returns_none(self):
        result = extract.parse_response('["name", "age"]')
        self.assertIsNone(result)

    def test_extra_unexpected_field_is_ignored(self):
        raw = (
            '{"name": "A", "age": "", "course_name": "", "contact": "", '
            '"email": "", "notes": "unexpected extra field"}'
        )
        result = extract.parse_response(raw)
        self.assertNotIn("notes", result)
        self.assertEqual(set(result.keys()), set(extract.FIELDS))


if __name__ == "__main__":
    unittest.main()
