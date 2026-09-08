import unittest
from unittest.mock import patch

from src.subagents import ethernet


class TestEthernetSubagent(unittest.TestCase):
    @patch("src.subagents.ethernet.answer_from_index")
    def test_answer_calls_answer_from_index_with_its_own_config(self, mock_answer_from_index):
        # Fake answer_from_index's return value -- we're not testing RAG
        # here, just that ethernet.answer() wires its own INDEX_DIR and
        # SYSTEM_PROMPT into the shared function correctly.
        mock_answer_from_index.return_value = {
            "answer": "fake answer",
            "pages_referenced": [[1, 2]],
        }

        result = ethernet.answer("What is the max cable length for 1000BASE-T?")

        mock_answer_from_index.assert_called_once_with(
            "What is the max cable length for 1000BASE-T?",
            ethernet.INDEX_DIR,
            ethernet.SYSTEM_PROMPT,
        )
        self.assertEqual(result["answer"], "fake answer")


if __name__ == "__main__":
    unittest.main()