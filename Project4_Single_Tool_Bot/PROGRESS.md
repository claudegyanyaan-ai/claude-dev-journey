# Project 4 — Single-Tool Bot — Progress Notes

**Finished:** 2026-08-20
**Confidence (1–5):** 3/5

## What I built
A CLI bot (`src/main.py`) that answers questions using Claude, with access
to one custom tool: a calculator (add, subtract, multiply, divide, power,
log). Claude decides whether a question needs the tool or can be answered
directly. First project built via the hybrid workflow — mentor drafted the
spec, sent through Claude Code, reviewed the diff on the two trickiest
points, then hand-wrote the tests.

## What I learned
- The tool_use loop: define a tool schema → send it via `tools=[...]` →
  check `response.stop_reason` to see if Claude wants to call the tool →
  if so, run the real function yourself → send a second API call with the
  full conversation plus a `tool_result` block → get Claude's final answer.
- Claude decides whether to use a tool — the code just reacts to
  `stop_reason`. The tool's `description` field is what actually
  influences that decision (worth writing carefully).
- The Claude API is fully stateless between calls — nothing is
  "remembered" automatically. Every call must resend the whole
  conversation history for the model to have that context, which is why
  the tool_use loop needs two separate `messages.create()` calls.
- `**dict` unpacking a tool's input arguments directly into a Python
  function call, relying on matching parameter/schema field names.

## Pitfalls / open items
- Folder named `Project4_Single_Tool_Bot`, breaking the established
  `04-name` numbering convention — confirmed intentional, not a mistake,
  but tracking now uses this exact name going forward.
- **Resolved (2026-08-20):** confirmed `"2+2"` does trigger the calculator
  tool (`stop_reason == "tool_use"`), rather than being answered directly
  from Claude's own knowledge.
- Didn't confirm outputs for the "no tool needed" (capital of France) or
  forced-error (divide by zero) test cases — still open if you want full
  coverage, but lower priority now that the main tool-selection question
  is answered.

## Still a bit shaky
- General coding/API depth — intentionally lighter per the hybrid
  workflow decision from Project 3.

Full session transcript: see `chat-logs/2026-08-20_1038.md`.
