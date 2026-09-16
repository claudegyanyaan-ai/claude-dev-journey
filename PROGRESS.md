# Claude Developer Journey — Progress

Goal: broad, practical literacy in directing Claude to build real projects — understanding what gets built, why, and how the pieces fit together. (Revised 2026-08-23 — see workflow note below. Originally aimed at Anthropic's Claude Certified Developer – Foundations exam; that target was deliberately dropped.)

## Status
- Current tier: 4 / 4
- Current project: Project 13 (not started, Ship It)
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

## Workflow note (2026-08-25) — Project 8's OCR pivot: don't trust "it ran" as "it worked"
Project 8 (RAG Docs Assistant) hit a real, unplanned detour: the source
PDF's text was supposed to be plainly `pypdf`-extractable per the spec, but
`pypdf` silently recovered under 10% of the document's actual content
(confirmed independently with two more extraction libraries, then by
literally rendering a page and looking at it — the text was embedded as
vector graphics, not real characters). No error was ever raised anywhere
in that chain; the bad extraction looked completely successful. Pivoted to
local OCR (PyMuPDF + Tesseract) after the user explicitly declined a paid
Claude-vision-transcription alternative once the cost tradeoff was
concrete. Worth carrying forward as a standing instinct, not just a
Project-8-specific fix: **a tool completing without an error says nothing
about whether its output is correct** — cross-check against ground truth
early, especially for anything parsing/extracting real-world files.

## Workflow note (2026-09-06) — an auth error that wasn't one, and a bug only Windows could show
Project 9 (Guardrailed Automation Agent) surfaced two lessons worth
carrying forward, both only visible because of testing against a real
environment rather than trusting a green run. First: a
`401 Unauthorized` from Anthropic's API isn't proof a key is bad — one
sandboxed shell used mid-build had its own network proxy silently
intercepting requests to `api.anthropic.com` and returning a plain-text
401 of its own before the request ever reached Anthropic. The actual tell
was the error's *shape*, not its status code: Anthropic's real auth
errors come back as JSON with a `type: authentication_error` body; this
didn't. Second: `store.py`'s Excel logic passed every test in the (Linux)
build environment, then failed 5 of them the moment the user ran the same
suite on their own Windows machine — `openpyxl`'s `read_only=True` mode
leaves a zip file handle open until closed explicitly, which Windows
enforces during cleanup and Linux doesn't. Neither issue was catchable
without running on the real target environment; "tests pass" and "tests
pass where this will actually run" are not the same claim.

## Workflow note (2026-09-09) — a hook that looked wired up but never fired, and a stale git lock
Project 11 (Eval & Observability Harness) surfaced two more "green doesn't
mean working" lessons. First: after wiring a `PreToolUse` hook
(`check-eval-before-commit.sh`) to gate `git commit` on a fresh eval run, a
test commit went through instantly with no `Eval gate: ...` message at
all — easy to misread as success. It wasn't: Claude Code's `PreToolUse`
hooks only intercept tool calls Claude Code's own agent makes through its
Bash tool; they have zero visibility into a `git commit` typed directly
into a terminal by a human. That's a real, permanent scope limit, not a
bug — a genuine git-level `.git/hooks/pre-commit` script would be needed to
gate *every* commit regardless of who runs it. The hook's own logic (command
filtering, venv-Python path resolution, fail-closed blocking when the eval
can't run) was verified independently by feeding it simulated input
directly; the success-path message (a real 15/15 run allowing the commit)
is still unverified pending an actual Claude-Code-driven commit on the
user's machine — flagged as an open item, not assumed to work.
Second: three git commits in a row failed with `Unable to create
'.git/index.lock': File exists` — traced to a genuinely stale lock file
(timestamped over a day old, 0 bytes, from some earlier interrupted git
process), confirmed safe to delete by checking its age before removing it.
Also discovered mid-session: `.claude/` is deliberately write-protected
from remote/device-bridge file delivery (a safety boundary against a
session silently installing its own hooks) — the new hook script and
`settings.json` had to be handed to the user as files and placed manually,
same as any other privileged config change.

## Workflow note (2026-09-14 to 2026-09-16) — Project 12's deployment: OS-level deps, import timing vs. compute cost, and a spec/workflow conflict
Project 12's deployment step surfaced three lessons worth carrying
forward. First: a dependency that shells out to an OS-level binary
(here, `pytesseract` -> `tesseract-ocr`) can't be satisfied by a native
Python-only host runtime at all, no matter what's in `requirements.txt`
-- Docker isn't just "more control," it's the only way to install a
non-Python system binary at all on Render. Second, and more subtle:
deferring a heavy import (`sentence_transformers`, pulling in `torch`)
from module level into the function that uses it only moves *when* its
memory cost is paid, not *how much* it costs -- the app stopped
OOM-crashing at startup, then crashed on the very first real request
instead, because the actual computation still needed more memory than
the instance had. The real fix was swapping the underlying runtime
(`fastembed`/ONNX Runtime in place of PyTorch) to lower the cost itself.
Third: Project 12's own spec ("GitHub Actions and automated PR/code
review -- usable directly on the team's shared repo") assumes Pull
Requests, but `TEAM_WORKFLOW.md` has this team pushing straight to
`main` with none -- a genuine conflict between a project's spec and this
team's actual, deliberately-chosen workflow, not a bug in either.
Resolved by treating one real test PR as a deliberate, one-off learning
exercise rather than silently adapting the workflow to trigger on push
instead (which would satisfy the letter of "automate reviews" while
quietly dropping "PR" from the requirement). That GitHub Actions piece
was built, then reverted at the user's request before the manual setup
steps were completed, and is being carried forward as explicitly open,
not abandoned.

## Completed Projects
| # | Project | Finished | Confidence (1–5) | Notes |
|---|---------|----------|-------------------|-------|
| 1 | Hello, Claude Code | 2026-08-18 | 4/5 | git init/add/commit, .env + .gitignore, venv, first live Claude API call. Full notes in `01-hello-claude-code/PROGRESS.md`. |
| 2 | CLI To-Do App | 2026-08-19 | 4/5 | Spec-writing for Claude Code, reviewing diffs in Manual mode, unittest with test isolation, git commit hygiene (amend). Full notes in `02-cli-todo-app/PROGRESS.md`. |
| 3 | Structured Data Extractor | 2026-08-19 | 3/5 | System prompts vs. user messages, JSON output validation, error handling. Workflow pivot to hybrid approach happened mid-project. Full notes in `03-structured-data-extractor/PROGRESS.md`. |
| 4 | Single-Tool Bot | 2026-08-20 | 3/5 | Tool_use loop (stop_reason, stateless second call, ** unpacking), first hybrid-workflow project. Folder named `Project4_Single_Tool_Bot` (deviation from numbering convention, intentional). Confirmed "2+2" triggers the calculator tool. Full notes in `Project4_Single_Tool_Bot/PROGRESS.md`. |
| 5 | Multi-Tool CLI Assistant | 2026-08-21 | 4/5 | Two-tool agent loop (calculator + real Open-Meteo weather), retry logic, multi-block tool_use batching, live non-determinism/evals lesson. Caught a FIFA World Cup 2026 hallucination (bot has no date awareness). Full notes in `05-multi-tool-cli-assistant/PROGRESS.md`. |
| 6 | Your First MCP Server | 2026-08-22 | 4/5 | Real MCP server (dictionary: English definitions + English→Hindi translation) via `mcp[cli]`, `@mcp.tool()` decorators, stdio transport, verified end-to-end via the MCP Inspector. First project built fully Claude-writes (workflow switched mid-project). Hit and fixed a real SDK version gap (`FastMCP` renamed `MCPServer` in `mcp==2.0.0`). Extensive follow-up Q&A on MCP mechanics (client/server model, connection handshake, multi-tool pooling, why no API key, what `mcp dev` does) before closing out — this project is also where the certification target got dropped (see workflow note above). Full notes in `06-your-first-mcp-server/PROGRESS.md`. |
| 7 | Claude Code Extensibility Lab | 2026-08-23 | 4/5 | Three repo-root `.claude/` customizations active for all future projects: `code-explainer` subagent (read-only, least-privilege tool scoping), `/update-logs` slash command (`disable-model-invocation` for a file-writing command), and a fail-open `PostToolUse` push-reminder hook (`matcher` + `if` layered filtering, never auto-pushes on this shared repo). Deliverable lives outside its own project folder by design — first project whose value is entirely reuse across the rest of the ladder. Real discovery mid-build: a new subagent/command/hook is invisible to the session that created it (Claude Code reads `.claude/` once, at startup) — required a session restart to verify any of the three actually worked. Full notes in `07-claude-code-extensibility-lab/PROGRESS.md`. |
| 8 | RAG Docs Assistant | 2026-08-25 | conceptual close-out done by the user separately (not recorded in this session) | Full local RAG pipeline over `docs/osnr.pdf`: heading-based chunking, local `sentence-transformers` embeddings, in-memory cosine-similarity retrieval, grounded+cited answers via Claude Haiku 4.5. Major unplanned detour: `pypdf` recovered under 10% of the document's real text (embedded as vector graphics, not selectable characters) — pivoted to local Tesseract OCR after cross-checking three extraction libraries and rendering a page to confirm visually; recovered ~11x more text. `chunk.py`'s 14 synthetic unit tests all passed yet still missed two real bugs only found by running against the actual OCR'd document (a regex collision between two different OCR artifacts, and a duplicated-heading variant that also duplicated a body line). All four of the spec's manual grounding/citation verification checks passed, including a word-for-word match against one of the document's own Self-Assessment Questions. Closed out with a project-scoped Claude Code skill (`ask-osnr-docs`) — drafted by the user independently, reviewed and fixed (path, stale facts, missing Tesseract prerequisite). Full notes in `08-rag-docs-assistant/PROGRESS.md`. |
| 9 | Guardrailed Automation Agent | 2026-09-06 | 3.5/5 | Full pipeline: `extract.py` (Claude-backed, verbatim-only field extraction — never guesses a missing value) → `guardrail.py` (pure auto-write/needs-confirmation logic: completeness, age plausibility, email shape, case-insensitive duplicate check) → `store.py` (safe append-only Excel read/write) → `agent.py` (the CLI tying it together, pausing for a real `[y/N]` human decision whenever guardrail says to). 39 unit tests across the four modules. Two real bugs caught only by testing against the real environment, not the sandbox that built it: a network proxy silently faking a `401 Unauthorized` before requests reached Anthropic, and a Windows-only `openpyxl` file-lock invisible on Linux (see workflow note above for both). Full notes in `09-guardrailed-automation-agent/PROGRESS.md`. |
| 10 | Multi-Agent Orchestration | 2026-09-08 | 3/5 (self-assessed; formal conceptual close-out check skipped by request) | Orchestrator/subagent pattern: `rag_core.py` (OCR-or-plain extraction, structure-agnostic chunking, embedding, retrieval, grounded answering — generalized from Project 8 to serve three documents) → three domain subagents (`dwdm_osnr`, `ethernet`, `ip`), each its own index/system prompt → `orchestrator.py` (Claude-based domain classification + routing, with a full execution trace: domain, source PDF, exact pages referenced) → `main.py` (interactive loop, one isolated context per question). Real bugs caught: `dwdm_osnr.pdf` had the same vector-graphics-text problem as Project 8's PDF (confirmed byte-identical); a chunk-boundary truncation bug fixed by widening the chunk window (800/150 → 1200/300), which also improved another subagent's answers as a side effect; a corrupted `requirements.txt` (UTF-16 + stray shell-command lines). Also shipped a repo-root `/ask-network` slash command. 4 unit tests passing. This project's PLAN.md "also covers" items — Routines (scheduled prompts) and headless mode — were explicitly skipped, not pursued. Closed out 2026-09-09 with `rebuild_indexes.py`, a scripted build for all three indexes (previously a manual one-off — see Project 11's row below). Full notes in `10-multi-agent-orchestration/PROGRESS.md`. |
| 11 | Eval & Observability Harness | 2026-09-09 | 3.5/5 (self-assessed) | 15-case eval suite (`eval_cases.json` + `run_eval.py`) scoring the Project 10 orchestrator's domain routing and answer content, one case run at a time through `route()`, writing a timestamped JSON report per run — verified 15/15 both from console output and by reading the saved report back independently. Also built this project's "also covers" items: a `PreToolUse` Claude Code hook (`check-eval-before-commit.sh`) that reruns the full eval before allowing `git commit` and blocks (exit 2) below a 100% threshold or if the eval can't run at all — gating on a fresh real result instead of a self-report. Real discovery: the hook never fires for a `git commit` typed directly into a terminal, only for one Claude Code's own agent runs itself — a materially different (and narrower) scope than a real git-level `pre-commit` hook; the success-path message is still unverified pending a real Claude-Code-driven commit (see 2026-09-09 workflow note above). Also hit and fixed a genuinely stale `.git/index.lock` blocking all commits, and discovered `.claude/` is write-protected from remote file delivery by design. Three atomic commits: `rebuild_indexes.py` (Project 10 gap-closer), the eval harness itself, and the gating hook. Full session notes in `chat-logs/2026-09-09_1412.md`. |
| 12 | Full-Stack Claude App | 2026-09-16 | 3/5 (self-assessed) | FastAPI + Postgres backend (RAG ingest/retrieve/answer, auth, orchestrator + 4 subagents, MCP server) and a Next.js frontend (auth, topic Q&A, upload modal, PWA support), fully deployed: a Docker-based Render backend (needed for the `tesseract-ocr` OS-level dependency) and a Vercel frontend, with CORS tightened to the real deployed origin. Real deployment detour: Render OOM-crashed under `sentence-transformers`/`torch` even after deferring its import to first use -- fixed by switching to `fastembed` (ONNX Runtime, same model, far less memory; see 2026-09-14->16 workflow note above). The "also covers" GitHub Actions/automated-PR-review item was built, then explicitly reverted and deferred rather than dropped, after finding it conflicts with the team's no-PR workflow. Close-out check: 1 of 3 questions answered cleanly, 2 needed correction -- CORS-vs-authentication is flagged as a new shaky concept, not confirmed understanding. Full session notes in `12-full-stack-claude-app/chat-logs/2026-09-12_1006.md` and `2026-09-16_1005.md`. |

## Concepts I still find shaky
- Environment variable lookup order beyond a single simple `.env` file.
- Full range of Claude API error types beyond 400 (credit) / 401 (auth) — e.g. rate limits, overloaded errors.
- Git commit hygiene — running `git status` before committing (mostly fixed in Project 4, keep watching).
- Claude Code hook scope — a `PreToolUse`/`PostToolUse` hook only sees tool calls Claude Code's own agent makes, never commands typed directly into a terminal. Needed a full explanation rather than landing on it independently during Project 11's close-out; revisit if it comes up again.
- CORS vs. authentication — CORS is a browser rule about which origins' JavaScript can call an API and read the response, independent of whatever auth check the server runs per request. Answered incorrectly as "restricts login" during Project 12's close-out -- a real gap, not just imprecise phrasing; revisit if it comes up again.

## Next session plan
- Kick off Project 13: Ship It (containerize with Docker, deploy to a real host, manage secrets/env vars, watch cost/rate limits) — concept area: deployment, cost/model optimization. Also covers: Plugins (packaging the team's trusted setup so everyone installs the same working configuration). Worth flagging up front: Project 12's own deployment step already covered Docker, real-host deployment, and secrets/env-var management hands-on — the genuinely new ground here is cost/rate-limit management and the Plugins piece, not re-teaching what's already been done.
- Open item carried over from Project 11: the eval-gating hook's success path (a real 15/15 run allowing a commit through) hasn't been verified with an actual Claude-Code-driven commit yet — still open, still not blocking anything.
- Open item carried over from Project 12: GitHub Actions / automated PR review was built, then reverted at the user's request (see 2026-09-14->16 workflow note) — pick back up whenever ready, including the one deliberate test PR needed to actually watch it fire.
