"""agent.py's orchestration logic, with extract/store I/O mocked or isolated.

extract.extract_from_file makes a real API call, so it's mocked here. store's
append_row/load_rows do real file I/O, but every test points spreadsheet_path
at its own tempfile.TemporaryDirectory() -- never the real enrollments.xlsx --
so guardrail.evaluate() and store.py run for real underneath.
"""

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import agent  # noqa: E402
import store  # noqa: E402


def make_lead(**overrides):
    lead = {
        "name": "Priya Sharma",
        "age": "28",
        "course_name": "Advanced Python for Data Science",
        "contact": "98765-43210",
        "email": "priya.sharma88@gmail.com",
    }
    lead.update(overrides)
    return lead


class TestProcessEmailAutoWrite(unittest.TestCase):
    def test_complete_lead_auto_writes_without_asking(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "enrollments.xlsx")
            with mock.patch("extract.extract_from_file", return_value=make_lead()), \
                 mock.patch("agent.confirm") as mock_confirm:
                result = agent.process_email("fake_email.txt", spreadsheet_path=path)

            mock_confirm.assert_not_called()
            self.assertTrue(result)
            self.assertEqual(len(store.load_rows(path)), 1)


class TestProcessEmailNeedsConfirmation(unittest.TestCase):
    def test_confirmed_pause_writes_the_row(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "enrollments.xlsx")
            lead = make_lead(age="")  # missing field -> needs_confirmation
            with mock.patch("extract.extract_from_file", return_value=lead), \
                 mock.patch("agent.confirm", return_value=True):
                result = agent.process_email("fake_email.txt", spreadsheet_path=path)

            self.assertTrue(result)
            self.assertEqual(len(store.load_rows(path)), 1)

    def test_declined_pause_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "enrollments.xlsx")
            lead = make_lead(age="")
            with mock.patch("extract.extract_from_file", return_value=lead), \
                 mock.patch("agent.confirm", return_value=False):
                result = agent.process_email("fake_email.txt", spreadsheet_path=path)

            self.assertFalse(result)
            self.assertEqual(store.load_rows(path), [])


class TestProcessEmailExtractionFailure(unittest.TestCase):
    def test_none_from_extract_is_skipped_without_touching_the_spreadsheet(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "enrollments.xlsx")
            with mock.patch("extract.extract_from_file", return_value=None), \
                 mock.patch("agent.confirm") as mock_confirm:
                result = agent.process_email("fake_email.txt", spreadsheet_path=path)

            mock_confirm.assert_not_called()
            self.assertFalse(result)
            # Nothing should have been created at all -- not even a header.
            self.assertFalse(os.path.isfile(path))


class TestConfirmPrompt(unittest.TestCase):
    def test_yes_variants_return_true(self):
        for answer in ["y", "Y", "yes", "YES", " y "]:
            with mock.patch("builtins.input", return_value=answer):
                self.assertTrue(agent.confirm("Write?"))

    def test_blank_or_no_returns_false(self):
        for answer in ["", "n", "no", "whatever"]:
            with mock.patch("builtins.input", return_value=answer):
                self.assertFalse(agent.confirm("Write?"))

    def test_eof_returns_false(self):
        with mock.patch("builtins.input", side_effect=EOFError):
            self.assertFalse(agent.confirm("Write?"))


class TestDuplicateAcrossRuns(unittest.TestCase):
    def test_second_run_of_same_email_needs_confirmation_for_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "enrollments.xlsx")
            with mock.patch("extract.extract_from_file", return_value=make_lead()):
                agent.process_email("fake_email.txt", spreadsheet_path=path)
                with mock.patch("agent.confirm", return_value=False) as mock_confirm:
                    result = agent.process_email("fake_email.txt", spreadsheet_path=path)
                    mock_confirm.assert_called_once()

            self.assertFalse(result)
            self.assertEqual(len(store.load_rows(path)), 1)  # still just the first


if __name__ == "__main__":
    unittest.main()
