# Structured Data Extractor

## What this is
A command-line tool that takes messy, unstructured text describing a list of
items with quantities and prices, and uses the Claude API to extract it into
clean, validated JSON.

## Setup
1. Create and activate a virtual environment:
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your real Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your-real-key-here
   ```

## How to run
```
python src/main.py "milk 1 ltr 100rs, flour 2kg 200rs"
```
Prints the extracted data as formatted JSON, e.g.:
```json
[
  {"item": "milk", "quantity": "1 ltr", "amount": 100},
  {"item": "flour", "quantity": "2kg", "amount": 200}
]
```

## How it works
- A **system prompt** tells Claude exactly what JSON shape to return and to
  respond with only JSON, no extra text.
- The actual messy text is sent as the user message.
- The response is validated with `json.loads()` before being trusted — if
  Claude ever returns something that isn't valid JSON, the program prints a
  clear error instead of crashing or silently using bad data.

## How to run the tests
```
python tests/test_main.py
```
Tests `parse_response()` directly with both valid and deliberately invalid
JSON strings — no API call needed to run the tests.
