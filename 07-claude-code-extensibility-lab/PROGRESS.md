# Project 7 — Claude Code Extensibility Lab: Progress

**Finished:** 2026-08-23

**Confidence (1–5):** 4/5 _(three of four close-out questions — root-vs-
project scope, least-privilege tool restriction on the subagent, and the
deliberate no-auto-push boundary — were answered correctly right away, in
own words, with the right underlying reasoning. The fourth, why a new
subagent/command/hook is invisible to the session that created it, needed
one hint before landing — a fair gap, since it's about Claude Code's own
internal timing rather than something inferable from the files themselves.)_

## What I built

Three repo-root `.claude/` customizations, active for every project from
here on (8–15), not just this one:

- `agents/code-explainer.md` — a read-only subagent (`Read, Grep, Glob`
  only) that explains the non-obvious parts of code, at a level suited to
  broad literacy rather than deep coding fluency.
- `commands/update-logs.md` — the `/update-logs` slash command, which
  finds the active project folder and appends/creates a dated
  `chat-logs/*.md` entry in this repo's established narrative style.
- `hooks/post-commit-push-reminder.sh` + `settings.json` — a `PostToolUse`
  hook, scoped via `matcher: "Bash"` plus `if: "Bash(git commit *)"`, that
  reminds (never blocks, never auto-pushes) when the branch is ahead of
  its upstream after a commit.

Plus this project's own `README.md` documenting and demonstrating all
three, since the actual deliverable lives outside this folder.

## What I learned

- **Claude Code reads `.claude/agents/`, `.claude/commands/`, and
  `.claude/settings.json` once, at session startup** — not continuously.
  A file created mid-session is invisible to that session no matter how
  long it keeps running; a fresh session is required to pick it up. This
  wasn't something we anticipated in the plan — it surfaced by actually
  trying to invoke the freshly-created subagent and command and watching
  both fail with "not found" / "unknown command."
- **Hooks are Claude-Code-specific, not real git hooks.** They only fire
  on Bash calls Claude Code itself makes through its own tool — running
  `git commit` in a separate terminal never triggers one.
- **Least privilege as a concrete design pattern**, not just an abstract
  security idea: restricting `code-explainer`'s tools to read-only, and
  `/update-logs`'s `disable-model-invocation: true`, make misuse
  *structurally impossible* rather than merely instructed against.
- **Layered filtering on the hook** — `matcher` (tool name) plus `if`
  (command content) plus the script's own redundant re-check — is a
  reasonable "defense in depth" pattern for scoping something that only
  wants to react to a narrow slice of activity.
- Auto-delegation to a subagent depends on how closely a request's
  phrasing matches its `description` — asking a broad conceptual question
  ("explain how MCP works") got answered directly by the main session
  rather than routed to `code-explainer`, since it read as concept-teaching
  rather than code-reading. A fuzzier boundary than expected going in.

## Pitfalls / open items

- A commit already existed for this project's exact files, already pushed,
  from earlier in this same session before a context-summary point —
  discovered mid-hook-test via `git log`, not something either side
  noticed beforehand. No content was lost (verified the prior commit's
  `PROGRESS.md` was the same unfinished stub), but it's a reminder that a
  long session's own internal state can drift out of sync with what's
  actually landed in git.
- The hook's "block until pushed" language in the original spec is
  softened in practice to "remind strongly" — `PostToolUse` fires *after*
  the commit already happened, so there's no actual undo available at that
  point; a true pre-commit block would need `PreToolUse` instead, which
  wasn't in scope here.

## Still a bit shaky

- The exact mechanics of *when* Claude Code re-scans `.claude/` — e.g.
  whether `/hooks` (mentioned in passing during research) forces a
  mid-session reload without a full restart — wasn't directly tested this
  round, just worked around via restarting.

Full session transcript: see `chat-logs/2026-08-23_1740.md`.
