# Project 7 — Claude Code Extensibility Lab

Unlike Projects 1–6, this project's deliverable isn't application code — it's
three reusable Claude Code customizations, added at the **repo root**
(`.claude/`) so they stay active for every future project (8–15), not just
this one. This folder documents and demonstrates them; it does not contain
the actual configuration.

## What it does

Three pieces, all living outside this folder at repo-root `.claude/`:

- **`code-explainer` subagent** (`.claude/agents/code-explainer.md`) — a
  read-only subagent that explains the non-obvious parts of code Claude Code
  just wrote or edited (logic, library quirks, design decisions), at a level
  suited to building broad practical literacy rather than deep coding
  fluency.
- **`/update-logs` slash command** (`.claude/commands/update-logs.md`) —
  finds the currently active numbered project folder and appends/creates a
  dated session log in its `chat-logs/` folder, in this repo's established
  prose-narrative style.
- **Post-`git commit` push reminder hook** (`.claude/settings.json` +
  `.claude/hooks/post-commit-push-reminder.sh`) — after a `git commit`
  Bash call, checks whether the branch is ahead of its upstream and, if so,
  surfaces a reminder. It never blocks and never runs `git push` itself —
  push stays a deliberate, reviewed step, which matters on this shared
  3-person repo.

## Setup

None needed for normal use — all three files are checked into the repo and
are active for any Claude Code session opened at the repo root.

**One real gotcha found while building this project**: a subagent, slash
command, or hook added or edited *during* a running session is not picked
up by that session — each is only registered when the session starts (and,
for hooks, only if `.claude/` already existed as a watched directory at
that time). If you add or change anything under `.claude/`, **start a new
Claude Code session** before expecting it to take effect.

## Usage

Demonstrating each piece (see "Known limitations" for the session-restart
caveat these all share):

1. **Subagent** — in a fresh session at the repo root, ask something like
   *"use the code-explainer subagent to explain
   06-your-first-mcp-server/src/server.py"* (or let auto-delegation trigger
   on a phrase like *"explain what this code does"* right after code is
   written/edited). Confirm it invokes `code-explainer` and the explanation
   skips boilerplate to focus on the non-obvious parts.
2. **Slash command** — type `/update-logs` (optionally with a project
   folder argument, e.g. `/update-logs 07-claude-code-extensibility-lab`).
   Confirm it identifies the active project, creates `chat-logs/` if
   missing, and writes/appends a dated file in the established narrative
   style.
3. **Hook** — make a commit (`git add` + `git commit -m "..."`). If the
   branch is ahead of its upstream, a reminder should appear; it should not
   block anything or run `git push`. Re-commit after pushing to confirm the
   reminder goes quiet once you're up to date, and run something unrelated
   like `git status` to confirm the hook stays silent for non-commit
   commands.

## How it works

1. **Subagent scoping.** `code-explainer`'s frontmatter restricts its
   `tools` to `Read, Grep, Glob` only — no `Write`, `Edit`, or `Bash` — so
   it is physically unable to modify anything, only read and explain code.
   Its `description` field doubles as the auto-delegation trigger: Claude
   Code matches incoming requests against that text to decide whether to
   invoke it on its own.
2. **Command permissions.** `/update-logs`'s `allowed-tools:
   Read, Write, Edit, Glob` pre-approves exactly those tools for its run,
   avoiding permission prompts without granting anything broader.
   `disable-model-invocation: true` means only a human typing `/update-logs`
   can trigger it — never Claude on its own — since it has file-writing
   side effects.
3. **Hook filtering and fail-open design.** In `settings.json`, `matcher:
   "Bash"` scopes the `PostToolUse` hook to Bash calls only; the
   handler-level `if: "Bash(git commit *)"` narrows that further to
   commands that actually look like `git commit ...`, so `git add`,
   `git status`, and unrelated Bash calls never trigger it. The shell
   script itself re-checks the command string as a second layer, then exits
   silently (`exit 0`, no output) if `git` isn't available or there's no
   upstream — "fail open," never breaking a session over a missing tool.
   It reports back via `{"additionalContext": "..."}` on stdout with no
   `decision` field, which surfaces the reminder without blocking anything.

## Known limitations

- **Session-restart requirement** (see Setup) — the most concrete lesson
  from this project: none of these three customizations take effect in the
  session that creates or edits them.
- **The hook can only remind, not literally block**, because `PostToolUse`
  fires *after* the Bash command already ran — there's no "undo" a hook can
  perform on a commit that already happened. A true pre-commit block would
  need a `PreToolUse` hook instead, which was out of scope here per the
  spec's explicit "reminder/block, never auto-push" requirement being
  satisfied by a reminder.
- **`/update-logs`'s project-detection is a heuristic** (root `PROGRESS.md`'s
  "Current project" line, cross-checked against numbered folders) — it asks
  rather than guesses when ambiguous, but still isn't a hard guarantee for
  unusual folder layouts.
- **`code-explainer` has no `Bash` access**, so it can only read and reason
  about code, never run it to confirm behavior — by design, since it's
  meant to be a read-only explainer, not a verifier.
- **Auto-delegation to `code-explainer` isn't guaranteed** — it depends on
  how closely a request's phrasing matches the subagent's `description`. A
  broad conceptual question (e.g. "explain how MCP works") is more likely
  to be answered directly by the main session than delegated.

## Demonstration

No automated test suite — this project is Claude Code configuration, not
application code, so verification is the manual walkthrough in **Usage**
above: invoke the subagent, run `/update-logs`, make a commit and observe
the hook, all after restarting the session so the new config is loaded.
