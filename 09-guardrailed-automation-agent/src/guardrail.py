"""Auto-write vs. needs-confirmation decision logic for one extracted lead.

Pure logic, no network or file I/O -- same "test in isolation" pattern as
extract.py's parse_response() and Project 8's chunk.py. Takes the existing
spreadsheet rows as a plain argument (a list of dicts) rather than reading
the spreadsheet itself, so it's testable with a hand-built fake list and has
no dependency on store.py.

Locked design (from the journey checkpoint):
  Auto-write only when all 5 fields are present, the age is plausible, the
  email is well-formed, and no existing row already has that email.
  Anything else pauses for human confirmation.
"""

import re

FIELDS = ["name", "age", "course_name", "contact", "email"]

# Plausibility bounds are a judgment call the checkpoint didn't pin a number
# to -- 10 covers the youngest realistic self-enrolling student (parents
# enrolling a 5-year-old, like the real implausible_age_01.txt sample, should
# pause for a human either way), 100 as a generous upper bound. Easy to
# adjust here if that's ever wrong for a real inquiry.
MIN_PLAUSIBLE_AGE = 10
MAX_PLAUSIBLE_AGE = 100

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def missing_fields(lead):
    """Return the list of FIELDS whose value is empty/missing, in order."""
    return [field for field in FIELDS if not lead.get(field)]


def is_age_plausible(age):
    """True if age parses as a whole number within the plausible range.

    A non-numeric or out-of-range age is NOT plausible -- including a blank
    age, which is already caught separately by missing_fields() but would
    otherwise crash int() here.
    """
    try:
        value = int(str(age).strip())
    except (ValueError, TypeError):
        return False
    return MIN_PLAUSIBLE_AGE <= value <= MAX_PLAUSIBLE_AGE


def is_email_well_formed(email):
    """True if email has a plausible local@domain.tld shape."""
    return bool(EMAIL_RE.match(str(email).strip()))


def find_duplicate_email(email, existing_rows):
    """Return the existing row whose email matches (case-insensitively), or None.

    existing_rows is a list of dicts, each expected to have an "email" key --
    the same shape store.py will eventually read from the spreadsheet.
    """
    target = str(email).strip().lower()
    if not target:
        return None
    for row in existing_rows:
        if str(row.get("email", "")).strip().lower() == target:
            return row
    return None


def evaluate(lead, existing_rows):
    """Decide whether `lead` can be auto-written, or needs human confirmation.

    Returns {"decision": "auto_write" | "needs_confirmation", "reasons": [...]}.
    `reasons` is empty exactly when decision is "auto_write" -- every pause
    comes with at least one human-readable reason, so agent.py can show the
    user why without re-deriving it.
    """
    reasons = []

    missing = missing_fields(lead)
    if missing:
        reasons.append(f"missing field(s): {', '.join(missing)}")

    # Only check age plausibility / email shape if the field is actually
    # present -- a missing field is already covered above, and running
    # is_age_plausible("") would just add a redundant second reason for the
    # same underlying problem.
    if lead.get("age") and not is_age_plausible(lead["age"]):
        reasons.append(f"age not plausible: '{lead['age']}'")

    if lead.get("email") and not is_email_well_formed(lead["email"]):
        reasons.append(f"email not well-formed: '{lead['email']}'")

    if lead.get("email") and is_email_well_formed(lead["email"]):
        dup = find_duplicate_email(lead["email"], existing_rows)
        if dup is not None:
            reasons.append(f"duplicate email: already enrolled as '{dup.get('name', '?')}'")

    decision = "needs_confirmation" if reasons else "auto_write"
    return {"decision": decision, "reasons": reasons}
