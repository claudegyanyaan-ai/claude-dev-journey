# Project 13 — Ship It

Concept area: deployment, cost/model optimization. Also covers: Plugins.

Project 12 already covered this project's original spec hands-on
(Docker, real-host deployment to Render, secrets/env-var management via
`.env` + Render's dashboard) — see its own `PROGRESS.md` note. So this
project's actual new ground is narrower and more focused:

1. **Cost / rate-limit management** — a per-user daily request cap and
   real (not estimated) token-usage/cost logging, added directly to
   Project 12's already-deployed FastAPI backend rather than a new app.
2. **Plugins** — packaging this repo's `.claude/` customizations
   (Project 7's subagent, slash command, hook) as an installable Claude
   Code plugin, not yet started as of this file.

## Part 1: Cost & rate limits (in `12-full-stack-claude-app/backend/`)

No new project folder for the code itself — the app only exists once,
so the new logic lives right next to what it protects:

- `rate_limit.py` — `check_rate_limit(username)`: raises HTTP 429 if a
  user has already made `DAILY_LIMIT` (10) `/ask` calls since midnight
  UTC today. Checked **before** Claude is ever called, so a blocked
  request costs nothing.
- `usage.py` — `log_usage(...)`: records one `/ask` call's real token
  spend (read off Claude's own `response.usage`, not guessed from
  question length) and its estimated cost, using Haiku 4.5's published
  per-token pricing.
- `db.py` — new `usage_log` table: one row per successful `/ask` call
  (username, timestamp, input/output tokens, api_calls, estimated cost
  in USD). This table is both the cost ledger and the rate limiter's
  source of truth — "how many today" and "how much did it cost" read
  from the same rows instead of two counters that could drift apart.
- `rag/answer.py` — now accumulates real token usage across every
  Claude API call a single question triggers (a multi-round tool-use
  search can mean more than one) and returns it alongside the answer.
- `main.py`'s `/ask` route — checks the rate limit first, calls the
  orchestrator, logs the real usage, and returns
  `requests_remaining_today` to the frontend.

**Design choice worth flagging**: the daily window resets at midnight
UTC (a calendar day), not a rolling 24 hours from each user's last
request — simpler to implement and reason about, and a reasonable
reading of "10 per day."

### To activate this on the real deployment

The Render backend and local dev both point at the same Neon Postgres
database, so the new `usage_log` table only needs to be created once,
from anywhere with the right `DATABASE_URL` — running `python db.py`
locally is enough; Render's redeployed code (after `git push`) will
find the table already there.

## Part 2: Plugin packaging

Not started yet.
