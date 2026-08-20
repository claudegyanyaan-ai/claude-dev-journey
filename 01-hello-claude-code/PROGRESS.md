# Project 1 — Hello, Claude Code — Progress Notes

**Finished:** 2026-08-18
**Confidence (1–5):** 4/5

## What I built
A minimal Python script (`src/main.py`) that loads an API key from `.env`,
creates an `anthropic.Anthropic()` client, sends one message to Claude via
`client.messages.create(...)`, and prints the reply.

## What I learned
- git basics: `init`, `add`, `commit`, `status`, `status --ignored`, `diff`,
  and that a terminal prompt/tab mismatch can make `cd` "silently fail"
  from your perspective even when nothing errors.
- `.gitignore` only protects *untracked* files going forward — it does not
  retroactively scrub something already committed. Order matters: write
  `.gitignore` before the sensitive file exists.
- Virtual environments (`.venv`) isolate a project's Python packages from
  the system-wide install; `requirements.txt` makes that environment
  reproducible without ever committing `.venv` itself.
- The Anthropic SDK reads `ANTHROPIC_API_KEY` from the environment
  automatically — `load_dotenv()` is what puts it there from `.env`.
- Reading API errors matters: a `400` about credit balance means the
  request worked and reached the server; a `401 authentication_error`
  would mean the key itself is wrong. Different fixes for each.

## Pitfalls I actually hit (so I remember them)
- Ran `cd` and `git init` in two different terminal tabs — `.git` ended up
  in the parent folder instead of the project folder.
- PowerShell blocked `.venv\Scripts\Activate.ps1` by default
  ("running scripts is disabled") — fixed with
  `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`.
- Briefly typed the placeholder text into `.env.example` instead of the
  real key into `.env` — no real leak, but a good reminder to double-check
  which file is open before typing secrets.
- Misread a billing error (`credit balance too low`) as a possible code
  bug at first — the `request_id` in the traceback was the tell that the
  request actually reached Anthropic's servers successfully.

## Still a bit shaky
- Precisely how environment variable lookup order works when multiple
  `.env` files or shell-level env vars could apply (only touched the
  simple single-`.env` case so far).
- Full range of Claude API error types beyond 400/401 (e.g. rate limits,
  overloaded errors) — expect this to come up more in later projects.

Full session transcript: see `chat-logs/2026-08-18_1547.md`.
