import unittest
from unittest.mock import MagicMock, patch

from src.orchestrator import classify_domain


class TestClassifyDomain(unittest.TestCase):
    @patch("src.orchestrator.anthropic.Anthropic")
    def test_classify_domain_returns_valid_domain(self, mock_anthropic_cls):
        # Build a fake response shaped like a real Anthropic API response,
        # pretending Claude answered "ethernet" -- no real API call happens.
        fake_text_block = MagicMock()
        fake_text_block.type = "text"
        fake_text_block.text = "ethernet"

        fake_response = MagicMock()
        fake_response.content = [fake_text_block]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = fake_response
        mock_anthropic_cls.return_value = mock_client

        result = classify_domain("What is the max cable length for 1000BASE-T?")

        self.assertEqual(result, "ethernet")


if __name__ == "__main__":
    unittest.main()