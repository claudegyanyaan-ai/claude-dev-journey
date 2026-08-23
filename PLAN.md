# Claude Developer Mentor — Master Plan (Parts 2–7)

Part 1 (the mentor system prompt) lives in `CLAUDE.md` in this same folder
so Claude Code loads it automatically every session. This file holds the
rest of the plan for reference.

**2026-08-23 note:** This plan originally targeted Anthropic's Claude
Certified Developer – Foundations exam. That target was deliberately
dropped (see `PROGRESS.md`'s 2026-08-23 workflow note) — the actual goal
now is broad, practical literacy in directing Claude to build real
projects, not deep hands-on coding fluency or a formal certification. The
project ladder below is kept largely as-is, because it's still a sensible
sequence for building that literacy one concept at a time — but the
"cert domain" framing, the readiness checklist, and the exam-timeline
language have been removed or reworded throughout.

**2026-08-23 note (2) — "Claude Code in Action" course woven in:**
Anthropic hosts a free, self-paced course at that title
(anthropic.skilljar.com/claude-code-in-action) aimed at developers moving
from one-off Claude Code prompts to longer, less-supervised, team-wide
workflows — exactly where this project ladder is headed from Project 7
onward, and directly relevant given the shared 3-person GitHub repo. (Note:
a Coursera listing with the same title is actually the beginner "Claude
Code 101" content already completed — don't confuse the two.) Its 9
concepts — steering long sessions, a followed CLAUDE.md, verification
skills, permission modes, hooks, routines & headless mode, GitHub Actions
& code review, verifying unsupervised runs, and plugins — are woven into
Projects 7–15 below at their most natural point (see the "Also covers"
column) rather than run as a separate track. The course's own framing was
built around exam relevance, which no longer applies here, so that's been
stripped out.

---
## PART 2 — WHY THIS APPROACH

The highest-leverage way to build real literacy in directing Claude for
software projects is a stack of small, real, increasingly complex builds
— each one deliberately exercising one concept area (the Claude API,
custom tool use, MCP, agent development, Claude Code workflows,
deployment) — with Claude Code doing most of the actual typing and this
mentor doing the coaching, and you focused on understanding *what* got
built, *why* it's shaped that way, and how the pieces connect. The measure
of success is being able to explain and reason about each project
afterward, not being able to reproduce its code from memory.

---
## PART 3 — THE 15-PROJECT LADDER

Each tier deliberately layers on the previous one. Don't skip tiers even
if a project looks easy — the folder/workflow habits matter as much as
the concepts.

### Tier 1 — Foundations (Projects 1–3)
| # | Project | Focus | Concept area |
|---|---------|-------|-------------|
| 1 | Hello, Claude Code | Project scaffolding, .env + API key handling, first script calling the Claude API from VS Code via Claude Code, git init | Claude API basics |
| 2 | CLI To-Do App | Writing clear specs for Claude Code, iterative refinement, basic file I/O, argument parsing, testing by hand | Dev workflow / Claude Code fluency |
| 3 | Structured Data Extractor | Turning messy text into clean JSON via the API, system prompts, output validation, error handling | Structured outputs, prompt design |

### Tier 2 — Tool Use & MCP (Projects 4–7)
| # | Project | Focus | Concept area | Also covers (from "Claude Code in Action") |
|---|---------|-------|-------------|-------|
| 4 | Single-Tool Bot | One custom tool (e.g. a calculator or unit converter), JSON schema design, the tool_use → tool_result loop | Tool use | |
| 5 | Multi-Tool CLI Assistant | Several tools, tool routing/selection, retries and error handling, agent loop concept | Tool use, agent basics | |
| 6 | Your First MCP Server | Build a small MCP server (2–3 tools) with the MCP SDK, connect it into Claude Code/Claude Desktop | MCP | |
| 7 | Claude Code Extensibility Lab | Custom subagents, slash commands, and hooks inside Claude Code itself (.claude/agents, .claude/hooks, CLAUDE.md conventions) | Claude Code workflows | Steering long sessions (Plan Mode as a repeatable habit, directed compaction, the rewind menu); writing a lean CLAUDE.md that Claude actually follows; permission modes (which fits exploratory vs. routine vs. high-trust work); hooks (rules that must never be skipped, e.g. tests before commit) |

### Tier 3 — Production-Grade Agents (Projects 8–11)
| # | Project | Focus | Concept area | Also covers (from "Claude Code in Action") |
|---|---------|-------|-------------|-------|
| 8 | RAG Docs Assistant | Chunking, retrieval, citations, grounding answers in your own documents | Agent development | Verification skills — packaging this project's retrieval procedure as a reusable skill instead of re-explaining it each session |
| 9 | Guardrailed Automation Agent | An agent that takes real actions with permission boundaries, human-in-the-loop confirmation, safe failure behavior | Security & safe agent design | Permission modes in depth; calibrating how much you verify Claude's output based on how little you supervised the run |
| 10 | Multi-Agent Orchestration | Orchestrator + subagent pattern, session/context management across agents | Advanced agent development | Routines (scheduling prompts on Anthropic's own infrastructure) and headless mode (running Claude Code without the interactive UI, wired into a script/pipeline) |
| 11 | Eval & Observability Harness | Test cases, scoring, logging/tracing for one of your earlier agents; iterate on prompts using eval results | Evaluation & optimization | Verifying unsupervised runs; gating on real test results with hooks rather than Claude's self-report |

### Tier 4 — Capstone (Projects 12–15)
| # | Project | Focus | Concept area | Also covers (from "Claude Code in Action") |
|---|---------|-------|-------------|-------|
| 12 | Full-Stack Claude App | Small backend (FastAPI/Flask or Node/Express) + minimal frontend, using the API + one MCP tool + basic auth | Applied integration | GitHub Actions and automated PR/code review — usable directly on the team's shared repo |
| 13 | Ship It | Containerize (Docker), deploy to a real host, manage secrets/env vars, watch cost/rate limits | Deployment, cost/model optimization | Plugins — packaging the team's trusted setup (config + skills + hooks) so everyone installs the same working configuration instead of rebuilding it |
| 14 | Security Review | Red-team one of your own earlier agents: prompt-injection tests, data-boundary checks, permission audit, written findings | Security | Verifying unsupervised runs and hooks, applied specifically as security-critical gates |
| 15 | Capstone (your choice) | A project of your own design combining API + tool use + MCP + agent + eval + deployment — your portfolio piece and final rehearsal | Everything, integrated | Bring it together: a followed CLAUDE.md, hooks, the right permission mode, and (if useful) a packaged plugin the whole team can install |

---
## PART 4 — PER-PROJECT WORK INSTRUCTION TEMPLATE

Have Claude follow this shape for every single project — ask it to
restate this checklist at the start of a project if it drifts:

1. Objective (1 sentence) + the broad concept area it builds toward.
2. Pre-flight check — confirm what you already know vs. what's new before
   starting.
3. Folder/file scaffold, explained before creation, e.g. for Project 2:

```
02-cli-todo-app/
├── README.md          # what this project is and how to run it
├── .env.example        # placeholder for API key — never commit the real one
├── src/
│   └── main.py          # entry point
├── tests/
│   └── test_main.py     # covers the core behavior
└── PROGRESS.md          # what you learned, linked from the root tracker
```

4. Build loop — small steps; Claude Code writes, you review the diff and
   test it, every non-obvious line gets explained, one step at a time.
5. A short conceptual close-out check (a few questions about the shape
   and reasoning of what got built, not line-by-line code tracing) before
   moving on.
6. Debrief — what this taught you, common pitfalls, how it connects to
   the bigger picture.
7. Git commit with a clear message; update the root PROGRESS.md.

---
## PART 5 — PROGRESS TRACKER TEMPLATE

See the live copy in `PROGRESS.md` in this folder — this is just the
template it was seeded from:

```
# Claude Developer Journey — Progress
Goal: broad, practical literacy directing Claude to build real projects
## Status
- Current tier: 1 / 4
- Current project: 01-hello-claude-code
- Started: <date>
## Completed Projects
| # | Project | Finished | Confidence (1–5) | Notes |
|---|---------|----------|-------------------|-------|
|   |         |          |                   |       |
## Concepts I still find shaky
-
## Next session plan
-
```

---
## PART 6 — BROAD LITERACY CHECKLIST

A lighter-weight replacement for the old exam-readiness checklist — a
sense-check of whether the concepts are actually landing, not a
memorization bar. You should be able to talk through each of these in
your own words, using your own past projects as examples — no need to
reproduce code from memory:

- [ ] Explain the Claude API request/response cycle and system vs. user
      vs. assistant roles
- [ ] Explain what a tool's JSON schema is for, and walk through the
      shape of a tool_use → tool_result loop
- [ ] Explain what MCP is, and the difference between an MCP tool,
      resource, and prompt
- [ ] Explain what your MCP server (Project 6) does and how a client
      connects to and uses it
- [ ] Explain Claude Code's subagents, hooks, and slash commands, and
      when you'd reach for each
- [ ] Describe at least two prompt-injection / security risks and how
      an agent could guard against them
- [ ] Explain, in broad strokes, how you'd evaluate whether an agent's
      behavior is actually good
- [ ] Walk someone else through what it'd take to deploy one of your
      projects, including secrets handling
- [ ] Explain the difference between hands-on turn-by-turn steering and
      an autonomous goal/loop run, and when each is appropriate
- [ ] Explain what a hook is and give one example of a rule it should
      enforce that a CLAUDE.md instruction alone couldn't guarantee
- [ ] Explain what a plugin packages up and why a team would want one

If something here feels shaky, that's worth a conversation, not
necessarily a whole new project.

---
## PART 7 — GROUND RULES (things to watch for and correct if Claude drifts)

- If Claude hands you a finished file with no explanation of what
  matters in it, stop it and ask for the walkthrough.
- If a project feels too easy or too slow, say so — ask to adjust pace
  rather than silently coasting or grinding.
- If exam-prep framing (cert domains, readiness checklists, "fails the
  exam" language) creeps back in anywhere, flag it — that goal was
  deliberately dropped on 2026-08-23.
- If you want to type a piece of code yourself for the practice on any
  given project, just say so — the "Claude writes by default" rule is a
  default, not a restriction.
- The "Also covers" concepts woven into Projects 7–15 (2026-08-23) are a
  guide, not a hard requirement — if a project's natural flow doesn't
  need one of them, say so rather than forcing it in.
