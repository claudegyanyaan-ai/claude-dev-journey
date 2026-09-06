"""Hand-crafted leads/existing-rows -> verify the auto-write decision logic.

No spreadsheet or network involved -- guardrail.evaluate() takes plain dicts,
same "test pure logic in isolation" approach as extract.py's tests.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import guardrail  # noqa: E402


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


class TestAutoWrite(unittest.TestCase):
    def test_complete_plausible_lead_with_no_duplicate_auto_writes(self):
        result = guardrail.evaluate(make_lead(), existing_rows=[])
        self.assertEqual(result, {"decision": "auto_write", "reasons": []})

    def test_existing_rows_with_other_emails_do_not_block(self):
        existing = [{"name": "Someone Else", "email": "someone@else.com"}]
        result = guardrail.evaluate(make_lead(), existing_rows=existing)
        self.assertEqual(result["decision"], "auto_write")


class TestMissingFields(unittest.TestCase):
    def test_missing_age_pauses_for_confirmation(self):
        # The real missing_age_01.txt case from extract.py's own verification.
        lead = make_lead(age="")
        result = guardrail.evaluate(lead, existing_rows=[])
        self.assertEqual(result["decision"], "needs_confirmation")
        self.assertIn("missing field(s): age", result["reasons"])

    def test_multiple_missing_fields_are_all_named(self):
        lead = make_lead(age="", contact="")
        result = guardrail.evaluate(lead, existing_rows=[])
        self.assertIn("missing field(s): age, contact", result["reasons"])

    def test_missing_age_does_not_also_trigger_implausible_age_reason(self):
        lead = make_lead(age="")
        result = guardrail.evaluate(lead, existing_rows=[])
        implausible_reasons = [r for r in result["reasons"] if "not plausible" in r]
        self.assertEqual(implausible_reasons, [])


class TestAgePlausibility(unittest.TestCase):
    def test_implausible_young_age_pauses(self):
        # The real implausible_age_01.txt case: age 5, extracted verbatim by
        # extract.py -- rejecting it is guardrail's job, not extract's.
        lead = make_lead(age="5")
        result = guardrail.evaluate(lead, existing_rows=[])
        self.assertEqual(result["decision"], "needs_confirmation")
        self.assertIn("age not plausible: '5'", result["reasons"])

    def test_implausible_old_age_pauses(self):
        lead = make_lead(age="150")
        result = guardrail.evaluate(lead, existing_rows=[])
        self.assertEqual(result["decision"], "needs_confirmation")

    def test_boundary_ages_are_plausible(self):
        self.assertTrue(guardrail.is_age_plausible("10"))
        self.assertTrue(guardrail.is_age_plausible("100"))

    def test_non_numeric_age_is_not_plausible(self):
        lead = make_lead(age="twenty-eight")
        result = guardrail.evaluate(lead, existing_rows=[])
        self.assertEqual(result["decision"], "needs_confirmation")


class TestEmailWellFormed(unittest.TestCase):
    def test_malformed_email_pauses(self):
        lead = make_lead(email="not-an-email")
        result = guardrail.evaluate(lead, existing_rows=[])
        self.assertEqual(result["decision"], "needs_confirmation")
        self.assertIn("email not well-formed: 'not-an-email'", result["reasons"])

    def test_malformed_email_does_not_also_run_duplicate_check(self):
        # A malformed email can't be meaningfully compared for duplicates --
        # only one reason should fire, not a confusing second one.
        existing = [{"name": "X", "email": "not-an-email"}]
        lead = make_lead(email="not-an-email")
        result = guardrail.evaluate(lead, existing_rows=existing)
        dup_reasons = [r for r in result["reasons"] if "duplicate" in r]
        self.assertEqual(dup_reasons, [])


class TestDuplicateEmail(unittest.TestCase):
    def test_exact_duplicate_pauses(self):
        existing = [{"name": "Priya Sharma", "email": "priya.sharma88@gmail.com"}]
        result = guardrail.evaluate(make_lead(), existing_rows=existing)
        self.assertEqual(result["decision"], "needs_confirmation")
        self.assertIn("duplicate email: already enrolled as 'Priya Sharma'", result["reasons"])

    def test_duplicate_check_is_case_insensitive(self):
        existing = [{"name": "Priya Sharma", "email": "Priya.Sharma88@GMAIL.com"}]
        result = guardrail.evaluate(make_lead(), existing_rows=existing)
        self.assertEqual(result["decision"], "needs_confirmation")

    def test_find_duplicate_email_returns_none_when_no_match(self):
        existing = [{"name": "Other", "email": "other@example.com"}]
        self.assertIsNone(guardrail.find_duplicate_email("priya.sharma88@gmail.com", existing))


class TestMultipleReasons(unittest.TestCase):
    def test_missing_and_implausible_can_both_be_reported(self):
        lead = make_lead(age="", email="not-an-email")
        result = guardrail.evaluate(lead, existing_rows=[])
        self.assertEqual(len(result["reasons"]), 2)


if __name__ == "__main__":
    unittest.main()
