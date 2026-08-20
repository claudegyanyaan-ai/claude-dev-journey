# Claude Developer Mentor — Master Plan (Parts 2–7)

Part 1 (the mentor system prompt) lives in `CLAUDE.md` in this same folder
so Claude Code loads it automatically every session. This file holds the
rest of the plan for reference.

---
## PART 2 — WHY THIS APPROACH

Anthropic's Claude Certified Developer – Foundations exam is built for
engineers who ship on Claude — it tests the Claude API, custom tool use,
MCP, agent development, and Claude Code workflows in realistic, applied
scenarios, not trivia. That means the highest-leverage prep is exactly
what this document sets up: a stack of small, real, increasingly complex
builds, each one deliberately exercising one exam domain, with you doing
the typing and Claude doing the coaching. Treat the certification as a
lagging indicator — if you can build and explain all 15 projects unaided,
the exam takes care of itself. (Exact exam fees, format, and domain
weighting can change — confirm current details on Anthropic Academy / the
Claude Partner Network before you register.)

---
## PART 3 — THE 15-PROJECT LADDER

Each tier deliberately layers on the previous one. Don't skip tiers even
if a project looks easy — the folder/workflow habits matter as much as
the code.

### Tier 1 — Foundations (Projects 1–3)
| # | Project | Focus | Cert domain |
|---|---------|-------|-------------|
| 1 | Hello, Claude Code | Project scaffolding, .env + API key handling, first script calling the Claude API from VS Code via Claude Code, git init | Claude API basics |
| 2 | CLI To-Do App | Writing clear specs for Claude Code, iterative refinement, basic file I/O, argument parsing, testing by hand | Dev workflow / Claude Code fluency |
| 3 | Structured Data Extractor | Turning messy text into clean JSON via the API, system prompts, output validation, error handling | Structured outputs, prompt design |

### Tier 2 — Tool Use & MCP (Projects 4–7)
| # | Project | Focus | Cert domain |
|---|---------|-------|-------------|
| 4 | Single-Tool Bot | One custom tool (e.g. a calculator or unit converter), JSON schema design, the tool_use → tool_result loop | Tool use |
| 5 | Multi-Tool CLI Assistant | Several tools, tool routing/selection, retries and error handling, agent loop concept | Tool use, agent basics |
| 6 | Your First MCP Server | Build a small MCP server (2–3 tools) with the MCP SDK, connect it into Claude Code/Claude Desktop | MCP |
| 7 | Claude Code Extensibility Lab | Custom subagents, slash commands, and hooks inside Claude Code itself (.claude/agents, .claude/hooks, CLAUDE.md conventions) | Claude Code workflows (directly exam-relevant) |

### Tier 3 — Production-Grade Agents (Projects 8–11)
| # | Project | Focus | Cert domain |
|---|---------|-------|-------------|
| 8 | RAG Docs Assistant | Chunking, retrieval, citations, grounding answers in your own documents | Agent development |
| 9 | Guardrailed Automation Agent | An agent that takes real actions with permission boundaries, human-in-the-loop confirmation, safe failure behavior | Security & safe agent design |
| 10 | Multi-Agent Orchestration | Orchestrator + subagent pattern, session/context management across agents | Advanced agent development |
| 11 | Eval & Observability Harness | Test cases, scoring, logging/tracing for one of your earlier agents; iterate on prompts using eval results | Evaluation & optimization |

### Tier 4 — Capstone (Projects 12–15)
| # | Project | Focus | Cert domain |
|---|---------|-------|-------------|
| 12 | Full-Stack Claude App | Small backend (FastAPI/Flask or Node/Express) + minimal frontend, using the API + one MCP tool + basic auth | Applied integration |
| 13 | Ship It | Containerize (Docker), deploy to a real host, manage secrets/env vars, watch cost/rate limits | Deployment, cost/model optimization |
| 14 | Security Review | Red-team one of your own earlier agents: prompt-injection tests, data-boundary checks, permission audit, written findings | Security |
| 15 | Capstone (your choice) | A project of your own design combining API + tool use + MCP + agent + eval + deployment — your portfolio piece and final rehearsal | Everything, integrated |

---
## PART 4 — PER-PROJECT WORK INSTRUCTION TEMPLATE

Have Claude follow this shape for every single project — ask it to
restate this checklist at the start of a project if it drifts:

1. Objective (1 sentence) + cert domain it maps to.
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
│   └── test_main.py     # you write at least one test yourself
└── PROGRESS.md          # what you learned, linked from the root tracker
```

4. Build loop — small steps, you type, Claude coaches, one step at a
   time.
5. Checkpoint quiz (3–5 questions) before moving on.
6. Debrief — what this taught you, common pitfalls, exam relevance.
7. Git commit with a clear message; update the root PROGRESS.md.

---
## PART 5 — PROGRESS TRACKER TEMPLATE

See the live copy in `PROGRESS.md` in this folder — this is just the
template it was seeded from:

```
# Claude Developer Journey — Progress
Goal: Claude Certified Developer – Foundations, target date: <fill in>
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
## PART 6 — CERTIFICATION READINESS CHECKLIST

Before booking the exam, you should be able to do all of the following
without Claude's help, only from memory + your own past projects:

- [ ] Explain the Claude API request/response cycle and system vs. user
      vs. assistant roles
- [ ] Design a tool's JSON schema and walk through a full
      tool_use → tool_result loop
- [ ] Explain what MCP is, and the difference between an MCP tool,
      resource, and prompt
- [ ] Build and connect a minimal MCP server from scratch
- [ ] Explain Claude Code's subagents, hooks, and slash commands, and
      when to use each
- [ ] Describe at least two prompt-injection / security risks and how
      you mitigated them in Project 9 or 14
- [ ] Explain how you evaluated and improved an agent's behavior in
      Project 11
- [ ] Walk someone else through deploying your Project 13 app, including
      secrets handling

If any box is shaky, that's your next study session — not a new project.

---
## PART 7 — GROUND RULES (things to watch for and correct if Claude drifts)

- If Claude starts writing entire files for you without explanation,
  stop it and ask for the step-by-step version.
- If a project feels too easy, say so — ask to compress the tier rather
  than silently coasting.
- If you're falling behind the 3–5 month timeline, ask Claude for an
  honest re-plan rather than pushing through confused.
- Always confirm current exam cost, format, and domain weighting
  directly on Anthropic Academy before registering — certification
  programs evolve.
