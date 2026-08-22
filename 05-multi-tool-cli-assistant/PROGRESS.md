# Project 5 — Multi-Tool CLI Assistant — Progress Notes

**Finished:** 2026-08-21
**Confidence (1–5):** 4/5 *(mentor estimate — say the word if you'd rate it differently)*

## What I built
Extends Project 4's single-tool pattern to two tools with real Claude-driven
selection: a calculator (reused) and a `get_weather` tool hitting the real
Open-Meteo API (geocoding + forecast, no API key needed). Unlike Project 4's
fixed two-call structure, this uses a proper agent loop (`while True`) that
collects every `tool_use` block from a response before looping back, so
Claude can call zero, one, or both tools in a single turn.

## What I learned
- Real multi-tool selection: Claude decides per-question whether a tool is
  needed, and which one(s) — verified across a wide range of questions
  (math, weather, general knowledge, both at once).
- Retry logic for a real external API: 3 attempts, 1s fixed delay, no
  backoff — and the distinction between a network failure (retry) and a
  "city not found" result (don't retry, just report it gracefully).
- Why Project 4's fixed two-call structure breaks once there are multiple
  tools: grabbing only the first `tool_use` block would silently drop a
  second tool request, and the Claude API requires a matching `tool_result`
  for every `tool_use` block it sent — so the follow-up call would likely
  fail validation, not just give an incomplete answer.
- LLM non-determinism, concretely: ran the identical prompt ("what is 5
  divided by 0, and what's the weather in Tokyo?") twice — first run only
  called `get_weather` and silently dropped the division question; second
  run called both tools and answered both parts. This is why single-run
  testing isn't enough for AI-driven code — the proper term is **evals**:
  running the same case N times and checking the pass rate (distinct from
  regression testing, which re-tests after code changes).
- The bot has no awareness of the current date and can't look anything up,
  so it can be confidently wrong about anything near/after its training
  cutoff — caught live when it claimed the 2026 FIFA World Cup "hasn't
  happened yet."

## Pitfalls / open items
- Windows verification of the weather tool (Open-Meteo round trip) was
  started but never confirmed/pasted back before wrapping up the Mac
  session — worth a quick sanity check next time this project is opened on
  Windows, though the Mac-side verification was thorough.
- `get_weather` is intentionally not unit-tested — real network calls,
  would need mocking (a technique not covered yet).

## Still a bit shaky
- General coding/API depth — intentionally lighter per the hybrid workflow
  decision from Project 3.

Full session transcript: see `chat-logs/2026-08-21_1143.md`.
