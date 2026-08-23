# Project 6 — Your First MCP Server — Progress Notes

**Finished:** 2026-08-22
**Confidence (1–5):** 4/5 *(conceptual understanding of MCP mechanics — client/server model, connection handshake, transport, why no API key — is solid, per the extensive follow-up Q&A. Code-level tracing wasn't pursued; that's no longer this project's goal, see below.)*

## What I built
A real local MCP server — `src/server.py` — exposing two tools over stdio:
`lookup_english` (English definitions via the free dictionaryapi.dev) and
`translate_to_hindi` (English→Hindi via the free MyMemory API). Unlike
Projects 4/5, which hand-rolled a tool_use loop against the Claude API
directly, this project packages tools into a standalone server speaking
the actual Model Context Protocol — any MCP-aware client (Claude Desktop,
the MCP Inspector, etc.) can discover and call them without ever seeing
the code. Needs no `.env`/API key at all — a first for this project
series, since the server itself never calls the Claude API.

## What I learned
- The MCP client/server model: a server declares tools (name, docstring
  as description, schema built from type hints); a client connects,
  asks "what can you do," then calls tools as needed. Verified this is
  literally what the MCP Inspector was doing when testing — Inspector as
  client, `server.py` as server.
- The connection handshake and multi-server tool pooling: a client
  initializes, lists tools per server, and combines results from multiple
  servers into one menu internally — same "pick the right tool" idea as
  Projects 4/5, just scaled to independently-written server processes.
- Why stdio transport means exactly one dedicated client per running
  server process (a private pipe set up once at launch, not a
  listening/multi-connection socket) — confirmed hands-on via a
  comprehension question, wrong on the first pass ("it's local"), correct
  on the second ("dedicated pipe for one user").
- Real SDK-version drift, hit directly: the spec assumed `FastMCP`, but
  `mcp==2.0.0` (actually installed) renamed it to `MCPServer` — diagnosed
  by inspecting the installed package's real module structure rather than
  guessing, confirmed via the `mcp` CLI's own source.
- Why no API key is needed: `dictionaryapi.dev` and MyMemory are free,
  unauthenticated public APIs using IP-based rate limiting instead of
  per-key billing — a deliberate project choice, not a workaround.
- What `mcp dev src/server.py` actually does versus `python src/server.py`
  directly: `mcp dev` is specifically the human-testable wrapper that also
  launches the MCP Inspector bridge; running the file directly would just
  sit silently on stdio with nothing to interact with it.

## Workflow note — two real changes happened during this project
1. At Step 2, switched from "user writes, mentor coaches" to "Claude Code
   writes, user reviews/tests" for the rest of this project specifically
   (see the mid-project `AskUserQuestion` decision).
2. During close-out, that turned into a much bigger change: the
   certification-exam target for the whole "Claude dev journey" was
   dropped entirely, and Claude-writes became the standing default for
   all future projects, not just this one. Full reasoning in the root
   `PROGRESS.md`'s 2026-08-23 workflow note. As a direct consequence, the
   checkpoint quiz's four code-tracing questions (retry helper internals,
   schema generation, a hypothetical 500-error trace, a hypothetical
   missing-dict-key trace) were **not** answered — they tested exactly the
   kind of line-by-line code fluency that's no longer this project's goal.
   The one quiz question that *was* answered (stdio + multi-client) was a
   conceptual "why," not a code trace, and got a real, correct,
   self-corrected answer.

## Pitfalls / open items
- The four skipped code-tracing quiz questions are a known, deliberate
  gap now, not an oversight — consistent with the revised goal.
- `fetch_english_definition`/`fetch_hindi_translation` don't handle
  non-404 HTTP error codes (e.g. a 500) — flagged as an intentional,
  in-scope-boundary gap during Step 3, not fixed.

## Still a bit shaky
- Nothing coding-specific flagged here going forward — see the root
  `PROGRESS.md`'s revised "Concepts I still find shaky" list, which no
  longer targets deep coding fluency.

Full session transcript: see `chat-logs/2026-08-22_2054.md`.
