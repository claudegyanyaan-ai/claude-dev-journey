# Project 6 — Your First MCP Server (English↔Hindi Dictionary)

A local MCP (Model Context Protocol) server exposing two tools over
stdio: an English dictionary lookup and an English→Hindi translator.
Unlike Projects 1-5, there's no CLI script to run directly — this is a
server that other MCP clients (Claude Desktop, the MCP Inspector, etc.)
connect to and call tools on.

## What it does

- **`lookup_english(word)`** — looks up an English word's definition via
  the free [dictionaryapi.dev](https://dictionaryapi.dev) API. Returns up
  to 2 "part of speech: definition" lines, or a graceful "No definition
  found" message for unknown words.
- **`translate_to_hindi(word)`** — translates a single English word to
  Hindi via the free [MyMemory Translation](https://mymemory.translated.net)
  API, or a graceful "Translation unavailable" message if the API can't
  produce a usable translation.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate   # Windows Git Bash
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. No `.env` needed — this project calls no Claude API and needs no
   secrets, unlike Projects 1, 3, 4, and 5.

## Usage

This is an MCP server, not a standalone script — it's meant to be run by
an MCP client, not invoked directly for output.

- **MCP Inspector** (manual testing/dev):
  ```bash
  mcp dev src/server.py
  ```
  Opens a browser UI where you can call `lookup_english` and
  `translate_to_hindi` directly and see the tool schemas the server
  generated from the function signatures and docstrings.
- **Claude Desktop / another MCP client:** point its server config at
  `python src/server.py` (stdio transport).

## How it works

1. `src/server.py` defines two `@mcp.tool()`-decorated functions using
   the `mcp` SDK's `MCPServer` class. (Note: some MCP tutorials/specs
   reference an older `FastMCP` class name — the SDK version installed
   here, `mcp==2.0.0`, renamed it to `MCPServer`. Same interface, same
   decorator, same `.run()` default — just a different import path.
   Worth always checking the installed SDK version against what a guide
   assumes.)
2. Each tool is a thin wrapper: fetch from `lookups.py`, format the
   result, return the string. The docstring on each tool function is
   what an MCP client reads to decide when to call it — the same job
   the `description` field did in Projects 4/5's hand-written JSON tool
   schemas.
3. `src/lookups.py` holds all network + pure logic, kept separate from
   the server so the formatting functions are unit-testable without
   hitting real APIs.
4. Both fetch functions share a `_get_with_retry` helper (3 attempts, 1
   second fixed delay, no backoff) for transient network failures — but
   each defines its own "real" (non-retryable) failure differently: an
   HTTP 404 for the dictionary API, a non-200 `responseStatus` field
   inside an otherwise-normal response for the translation API (this API
   doesn't 404 on unknown words).
5. The server runs over stdio only (`mcp.run()`'s default) — it talks
   only to whatever process launches it directly. No HTTP/SSE transport,
   no custom client — both explicitly out of scope for this project.

## Known limitations

- Single-word lookups only — no phrases or sentences.
- No handling for HTTP error codes other than 404 (e.g. a 500 from the
  dictionary API would likely raise rather than fail gracefully) — out
  of scope per the spec, not an oversight.
- Two tools only, by design — no synonyms, example sentences, or audio
  pronunciation this round.
- MyMemory's free tier can return low-quality translations for uncommon
  words; the code only checks `responseStatus == 200` ("the API is
  confident enough to call this a real answer"), it doesn't judge
  translation quality itself.

## Tests

```bash
python -m unittest discover tests
```

Tests cover the two pure formatting functions (`format_definition`,
`format_translation`) against hand-built fake JSON — not the fetch
functions, which make real network calls (same reasoning Project 5 used
to exclude `get_weather` from its tests: properly testing them would
need mocking, not covered yet).
