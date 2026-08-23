import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import lookups


class TestFormatDefinition(unittest.TestCase):
    def test_none_returns_graceful_message(self):
        self.assertEqual(
            lookups.format_definition(None),
            "No definition found for this word.",
        )

    def test_empty_list_returns_graceful_message(self):
        self.assertEqual(
            lookups.format_definition([]),
            "No definition found for this word.",
        )

    def test_single_meaning(self):
        data = [
            {
                "word": "hello",
                "meanings": [
                    {
                        "partOfSpeech": "exclamation",
                        "definitions": [
                            {"definition": "used as a greeting."},
                        ],
                    }
                ],
            }
        ]
        self.assertEqual(
            lookups.format_definition(data),
            "exclamation: used as a greeting.",
        )

    def test_caps_at_two_meanings(self):
        data = [
            {
                "word": "run",
                "meanings": [
                    {"partOfSpeech": "verb", "definitions": [{"definition": "to move fast."}]},
                    {"partOfSpeech": "noun", "definitions": [{"definition": "an act of running."}]},
                    {"partOfSpeech": "adjective", "definitions": [{"definition": "operating."}]},
                ],
            }
        ]
        result = lookups.format_definition(data)
        self.assertEqual(
            result,
            "verb: to move fast. | noun: an act of running.",
        )
        self.assertNotIn("adjective", result)


class TestFormatTranslation(unittest.TestCase):
    def test_none_returns_graceful_message(self):
        self.assertEqual(
            lookups.format_translation(None),
            "Translation unavailable.",
        )

    def test_missing_translated_text_returns_graceful_message(self):
        self.assertEqual(
            lookups.format_translation({"responseData": {}}),
            "Translation unavailable.",
        )

    def test_normal_translation(self):
        data = {"responseData": {"translatedText": "नमस्ते"}}
        self.assertEqual(lookups.format_translation(data), "नमस्ते")


if __name__ == "__main__":
    unittest.main()
