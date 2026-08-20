# Single-Tool Bot

## What this is
A command-line bot that answers questions using Claude, with access to one
custom tool: a calculator (add, subtract, multiply, divide, power, log).
Claude decides on its own whether a question needs the calculator or can be
answered directly — this project demonstrates the core "tool use" loop.

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
3. Copy `.env.example` to `.env` and add your real Anthropic API key.

## How to run
```
python src/main.py "what is 15% of 340?"
```

## How it works
1. The question is sent to Claude along with a `calculator` tool definition
   (a JSON schema describing what the tool does and what inputs it needs).
2. Claude decides whether to answer directly or request the tool. If it
   requests the tool, the response's `stop_reason` is `"tool_use"`.
3. If the tool was requested, the code actually runs the real calculation
   (`run_calculator()`) and sends a **second** message to Claude containing
   the result — the API has no memory between calls, so the whole
   conversation (original question + Claude's tool request + the result)
   is resent each time.
4. Claude's final response — now informed by the real computed result — is
   printed.

## How to run the tests
```
python tests/test_main.py
```
Tests `run_calculator()` directly (add, divide-by-zero error handling, log
with default base) — no API call needed.
