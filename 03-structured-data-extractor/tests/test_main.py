import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import main


class TestParseResponse(unittest.TestCase):
    def test_valid_json_parses_correctly(self):
        raw = '[{"item": "milk", "quantity": "1 ltr", "amount": 100}]'
        result = main.parse_response(raw)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["item"], "milk")

    def test_invalid_json_returns_none(self):
        result = main.parse_response("this is not json")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()