"""Extract structured lead data from a single course-enrollment inquiry email.

Mirrors Project 3's extraction pattern (system prompt -> JSON, no markdown
fences, parse defensively) but with a stricter contract: every value must be
copied verbatim from the email text. Nothing is ever inferred or guessed --
a field that isn't literally present comes back as an empty string, so a
downstream guardrail can tell "stated" apart from "missing" with certainty.
"""

import os
import sys
import json
import argparse
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

FIELDS = ["name", "age", "course_name", "contact", "email"]

SYSTEM_PROMPT = (
    "You are a lead-extraction assistant for a course-enrollment inbox. "
    "The user will give you the raw text of one inquiry email. Extract "
    "exactly these fields into a JSON object: \"name\" (string), \"age\" "
    "(string), \"course_name\" (string), \"contact\" (string), \"email\" "
    "(string). Every value must be copied verbatim from the email text -- "
    "never infer, guess, calculate, or fill in a value that is not "
    "literally stated. If a field is not present in the email, its value "
    "must be the empty string \"\". Respond with ONLY the JSON object -- "
    "no explanation, no markdown code fences, no text before or after it."
)


def extract_lead(text):
    """Send one email's text to Claude, return its raw text response."""
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}],
    )
    return response.content[0].text


def _strip_code_fence(text):
    """Strip a leading/trailing markdown code fence, if present.

    The system prompt tells Claude not to use one, but haiku doesn't always
    comply -- observed in testing on 2 of 3 real sample emails. Stripping
    defensively here is cheaper than fighting the model for 100% prompt
    compliance, and this only ever removes fence markers, never touches
    the JSON content itself.
    """
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        lines = lines[1:]  # drop opening ``` or ```json
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines)
    return stripped


def parse_response(raw_text):
    """Parse Claude's raw response into a dict, or None if it isn't valid JSON.

    Also guards against a response that parses but is missing a field or has
    an unexpected shape -- fills any missing field with "" rather than
    letting a KeyError surface downstream, but still requires the result to
    be a JSON object at all.
    """
    try:
        data = json.loads(_strip_code_fence(raw_text))
    except json.JSONDecodeError as e:
        print("Error: Claude did not return valid JSON.")
        print(f"Details: {e}")
        print(f"Raw response was: {raw_text}")
        return None

    if not isinstance(data, dict):
        print("Error: Claude's JSON was not an object.")
        print(f"Raw response was: {raw_text}")
        return None

    return {field: str(data.get(field, "") or "") for field in FIELDS}


def extract_from_file(path):
    """Read an email file and return its extracted lead dict, or None."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    raw = extract_lead(text)
    return parse_response(raw)


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured lead data from a course-enrollment inquiry email."
    )
    parser.add_argument("email_file", help="Path to a .txt file containing one inquiry email.")
    args = parser.parse_args()

    if not os.path.isfile(args.email_file):
        print(f"Error: no such file: {args.email_file}")
        sys.exit(1)

    result = extract_from_file(args.email_file)
    if result is not None:
        print(json.dumps(result, indent=2))
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
