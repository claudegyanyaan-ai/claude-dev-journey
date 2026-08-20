# Project 2 — CLI To-Do App — Progress Notes

**Finished:** 2026-08-19
**Confidence (1–5):** 4/5

## What I built
A command-line to-do app (`src/main.py`) with `add`, `list`, `done`, and
`remove` commands, storing tasks in `tasks.json`. Built entirely by writing
specs for Claude Code and reviewing/testing its output in Manual permission
mode, plus one hand-written `unittest` test (`tests/test_main.py`).

## What I learned
- How to write a spec good enough for an AI coding agent: scope it small
  (one command at a time), state the exact interface, state exactly where
  data lives, and explicitly say what NOT to build yet.
- Manual permission mode in Claude Code shows a diff and waits for approval
  before touching any file — the deliberate checkpoint that makes reviewing
  AI-generated code possible instead of just trusting it.
- Why a CLI program needs a file (`tasks.json`) instead of a variable to
  "remember" anything — each run is a fresh process with no memory of the
  last one.
- Read-modify-write file pattern: read the whole file into memory, change
  it, write the whole thing back — used identically across add/done/remove.
- `enumerate(list, start=1)`, one-line conditional expressions
  (`x if cond else y`), and `argparse`'s `type=int` auto-validation.
- A genuine Python gotcha: negative list indexing (`tasks[-1]` wraps to the
  last item instead of erroring) — an upper-bound-only range check silently
  lets bad input through.
- `unittest` basics: `setUp`/`tearDown` for test isolation, temporarily
  repointing a module-level constant (`main.TASKS_FILE`) to a throwaway
  file so tests never touch real data.
- `git commit --amend` to fix the most recent commit's message — safe only
  because nothing had been shared/pushed yet.

## Pitfalls I actually hit (so I remember them)
- First attempt at writing a spec solo went off-topic (described sample
  data instead of an actual spec) — had to back up and build it via guided
  questions instead.
- Terminal still showed `(.venv)` from Project 1's environment even though
  this project has no venv — activation is a terminal-session property, not
  a per-folder one; `cd` doesn't undo it, only `deactivate` or a fresh
  terminal does.
- Skipped a commit after the `list` command, so it silently got bundled
  into the next commit (`done`) instead of having its own entry — not lost
  work, just messier history.
- Accepted the `remove` command's diff without reviewing it first — got
  away with it since it mirrored `done`'s structure, but flagged as a habit
  to hold the line on going forward.
- Reused an old commit message by mistake for the README commit — caught
  and fixed with `git commit --amend`.

## Still a bit shaky
- Drafting a spec from a blank slate without guided questions to scaffold it.
- Keeping the "review before accept" discipline once a pattern starts
  feeling repetitive/predictable.

Full session transcript: see `chat-logs/2026-08-19_1354.md`.
