# Claude Developer Journey — Progress

Goal: broad, practical literacy in directing Claude to build real projects — understanding what gets built, why, and how the pieces fit together. (Revised 2026-08-23 — see workflow note below. Originally aimed at Anthropic's Claude Certified Developer – Foundations exam; that target was deliberately dropped.)

## Status
- Current tier: 2 / 4
- Current project: Project 7 (not started, Claude Code Extensibility Lab)
- Started: 2026-08-18

## Workflow note (2026-08-19)
After Project 3, clarified the real goal is directing Claude Code effectively,
not deep coding fluency for its own sake. Checked what the actual CCDV-F exam
tests (hands-on API/coding integration is the largest domain; Claude Code
itself is a small slice) and agreed on a **hybrid path**: keep the
certification as the target, but shift future projects toward Project 2's
lighter-touch style (spec → review diff → test) even for new material,
typing less by hand. Tradeoff accepted knowingly: will need dedicated extra
practice in the coding-heavy exam domains before actually booking the exam —
flag this again as we approach Tier 3/4.

## Workflow note (2026-08-22)
Team plan changed again: Project 6 (Your First MCP Server) is now being
built by the user directly, not handed off to a teammate — noted so future
sessions don't assume the original 5/6/7 split still holds. Also cleaned up
cross-platform repo hygiene while closing out Project 5: added a root
`.gitattributes` (normalizes to LF) since Mac↔Windows checkouts were
producing whole-file "modified" diffs that were pure line-ending noise, and
committed `TEAM_WORKFLOW.md`, which had been written last session but never
actually pushed.

## Workflow note (2026-08-23) — dropped the certification target

During Project 6's close-out quiz, user was honest that they didn't want to
work through code-tracing questions — their actual goal was never deep
coding fluency, it's broad literacy in directing Claude to build projects:
understanding what gets built, why, and how it fits together. Since the
CCDV-F exam (per the 2026-08-19 note above) tests hands-on coding as its
*largest* domain, this created a real, direct conflict between the stated
goal and the actual exam requirements — not something to paper over. Asked
directly rather than assumed; user chose to **drop the certification target
entirely** and keep the broad-literacy path as the actual goal going
forward.

Consequences, applied immediately:
- `CLAUDE.md` and `PLAN.md` rewritten — all exam/certification framing
  removed (cert domains → "concept area," exam readiness checklist →
  lighter "broad literacy checklist," dropped exam timeline/cost language).
- Default workflow flipped for all future projects: **Claude Code writes
  the code by default**, user reviews the diff, tests it, gets every
  non-obvious line explained — the reverse of the original "user writes,
  mentor coaches" default. (This had already happened ad hoc for Project 6
  at Step 2; now it's the standing default, not a one-off.)
- Per-project close-out changes from a code-tracing quiz to a shorter
  conceptual check (shape/reasoning of what got built, not line-by-line
  code recall).
- The 15-project ladder itself is unchanged — still a sensible sequence
  for building broad literacy one concept at a time — only the framing
  and teaching style around it changed.
- `progress-dashboard.html` goal subtitle and an obsolete "review before
  the exam" line in the shaky-concepts list updated to match.

## Workflow note (2026-08-23b) — wove "Claude Code in Action" concepts into Projects 7-15
Reviewed Anthropic's live "Claude Code in Action" course
(anthropic.skilljar.com/claude-code-in-action) — distinct from the
similarly-titled Coursera listing, which is actually the beginner
"Claude Code 101" content already completed. It covers 9 concepts for
running longer, less-supervised, team-wide Claude Code workflows:
steering long sessions (Plan Mode, directed compaction, the rewind menu),
a CLAUDE.md that's actually followed, verification skills, permission
modes, hooks, routines & headless mode, GitHub Actions & code review,
verifying unsupervised runs, and plugins.
Decision (confirmed via AskUserQuestion): don't add a separate track for
this. Weave each concept into whichever of Projects 7-15 is the natural
fit instead, and strip the course's own exam-relevance framing, consistent
with the 2026-08-23 pivot away from the certification goal. The 3-person
team/shared-GitHub-repo setup is still current (Project 6 solo was a
one-off). Full mapping is in `PLAN.md` PART 3's new "Also covers" column;
three checklist items were also added to PART 6.

## Completed Projects
| # | Project | Finished | Confidence (1–5) | Notes |
|---|---------|----------|-------------------|-------|
| 1 | Hello, Claude Code | 2026-08-18 | 4/5 | git init/add/commit, .env + .gitignore, venv, first live Claude API call. Full notes in `01-hello-claude-code/PROGRESS.md`. |
| 2 | CLI To-Do App | 2026-08-19 | 4/5 | Spec-writing for Claude Code, reviewing diffs in Manual mode, unittest with test isolation, git commit hygiene (amend). Full notes in `02-cli-todo-app/PROGRESS.md`. |
| 3 | Structured Data Extractor | 2026-08-19 | 3/5 | System prompts vs. user messages, JSON output validation, error handling. Workflow pivot to hybrid approach happened mid-project. Full notes in `03-structured-data-extractor/PROGRESS.md`. |
| 4 | Single-Tool Bot | 2026-08-20 | 3/5 | Tool_use loop (stop_reason, stateless second call, ** unpacking), first hybrid-workflow project. Folder named `Project4_Single_Tool_Bot` (deviation from numbering convention, intentional). Confirmed "2+2" triggers the calculator tool. Full notes in `Project4_Single_Tool_Bot/PROGRESS.md`. |
| 5 | Multi-Tool CLI Assistant | 2026-08-21 | 4/5 | Two-tool agent loop (calculator + real Open-Meteo weather), retry logic, multi-block tool_use batching, live non-determinism/evals lesson. Caught a FIFA World Cup 2026 hallucination (bot has no date awareness). Full notes in `05-multi-tool-cli-assistant/PROGRESS.md`. |
| 6 | Your First MCP Server | 2026-08-22 | 4/5 | Real MCP server (dictionary: English definitions + English→Hindi translation) via `mcp[cli]`, `@mcp.tool()` decorators, stdio transport, verified end-to-end via the MCP Inspector. First project built fully Claude-writes (workflow switched mid-project). Hit and fixed a real SDK version gap (`FastMCP` renamed `MCPServer` in `mcp==2.0.0`). Extensive follow-up Q&A on MCP mechanics (client/server model, connection handshake, multi-tool pooling, why no API key, what `mcp dev` does) before closing out — this project is also where the certification target got dropped (see workflow note above). Full notes in `06-your-first-mcp-server/PROGRESS.md`. |

## Concepts I still find shaky
- Environment variable lookup order beyond a single simple `.env` file.
- Full range of Claude API error types beyond 400 (credit) / 401 (auth) — e.g. rate limits, overloaded errors.
- Git commit hygiene — running `git status` before committing (mostly fixed in Project 4, keep watching).

## Next session plan
- Kick off Tier 2, Project 7: Claude Code Extensibility Lab (custom subagents, slash commands, hooks) — using the new default workflow (Claude writes, conceptual close-out).
