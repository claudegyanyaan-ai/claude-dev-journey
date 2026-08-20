import os
import json
import anthropic
import argparse
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()
SYSTEM_PROMPT = (
    "You are a data extraction assistant. The user will give you messy, "
    "unstructured text describing a list of items with quantities and prices. "
    "Extract it into a JSON array where each object has exactly these fields: "
    '"item" (string), "quantity" (string), and "amount" (number, no currency '
    "symbols or text). Respond with ONLY the JSON array — no explanation, no "
    "markdown code fences, no text before or after it."
)
def extract_items(text):
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": text}]
    )
    return response.content[0].text
def parse_response(raw_text):
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"Error: Claude did not return valid JSON.")
        print(f"Details: {e}")
        print(f"Raw response was: {raw_text}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Extract structured data from messy text.")
    parser.add_argument("text", help="The messy text to extract data from.")
    args = parser.parse_args()

    raw_response = extract_items(args.text)
    result = parse_response(raw_response)

    if result is not None:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()