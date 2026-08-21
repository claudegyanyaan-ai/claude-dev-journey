# Project 5 — Multi-Tool CLI Assistant

A command-line assistant that can answer questions directly, or reach for one
of two tools when it needs to: a **calculator** and a **weather lookup**.
Unlike Project 4 (which had only one tool and a fixed two-call sequence),
this version uses a proper **agent loop** — it can call zero, one, or
multiple tools per question, and keeps looping until it has a final answer.

## What it does

Ask it a question. It decides for itself whether it needs a tool:

- Math questions (`"what is 15% of 340?"`, `"2 to the power of 10"`) → uses the **calculator** tool.
- Weather questions (`"what's the weather in Paris?"`) → uses the **get_weather** tool, which calls a real, free weather API (Open-Meteo, no API key required).
- General knowledge questions (`"what's the capital of France?"`) → answered directly, no tool used.
- Questions needing both at once (`"what's 5 divided by 0, and what's the weather in Tokyo?"`) → both tools can be called together in a single turn.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your Anthropic API key:
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and fill in `ANTHROPIC_API_KEY=your-key-here`.

## Usage

```bash
python src/main.py "what is 2 to the power of 10?"
python src/main.py "what's the weather in Tokyo?"
python src/main.py "what's 5 divided by 0, and what's the weather in Tokyo?"
```

## How it works (the agent loop)

1. Your question is sent to Claude along with the two tool definitions.
2. Claude either answers directly, or asks to call one or more tools.
3. If it asks for tools, the code actually runs them (the real calculator math, or a real HTTP call to Open-Meteo) and sends every result back to Claude in one message.
4. This repeats — Claude can ask for more tools after seeing a result — until it gives a final answer with no more tool requests.

This is different from Project 4's fixed "one call, maybe one tool, second call, done" structure: with two tools available, Claude might request both in one go, or across multiple rounds, so the code loops instead of assuming a fixed shape.

## Known limitations

- The weather tool retries failed network calls up to 3 times before giving up gracefully — it won't crash on a bad connection, but it will say the service is unavailable rather than hang forever.
- The bot has no built-in awareness of the current date, and no way to look up recent real-world events — it can be confidently wrong about anything after its training cutoff (see the FIFA World Cup 2026 example from testing this project — it incorrectly assumed the tournament hadn't happened yet).
- Each run is a single question in, single answer out — like Project 4, there's no memory across separate command-line runs.

## Tests

```bash
python -m unittest discover tests
```

Tests cover `run_calculator` directly (addition, divide-by-zero, and power) — not `get_weather`, since that makes real network calls and testing it properly would require mocking (a technique not covered in this project).