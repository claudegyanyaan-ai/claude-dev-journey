# Claude Developer Journey — Progress

Goal: Claude Certified Developer – Foundations, target date: Nov 2026 – Jan 2027 (3–5 months from 2026-08-18)

## Status
- Current tier: 2 / 4
- Current project: Project5 (not started, Multi-Tool CLI Assistant)
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

## Completed Projects
| # | Project | Finished | Confidence (1–5) | Notes |
|---|---------|----------|-------------------|-------|
| 1 | Hello, Claude Code | 2026-08-18 | 4/5 | git init/add/commit, .env + .gitignore, venv, first live Claude API call. Full notes in `01-hello-claude-code/PROGRESS.md`. |
| 2 | CLI To-Do App | 2026-08-19 | 4/5 | Spec-writing for Claude Code, reviewing diffs in Manual mode, unittest with test isolation, git commit hygiene (amend). Full notes in `02-cli-todo-app/PROGRESS.md`. |
| 3 | Structured Data Extractor | 2026-08-19 | 3/5 | System prompts vs. user messages, JSON output validation, error handling. Workflow pivot to hybrid approach happened mid-project. Full notes in `03-structured-data-extractor/PROGRESS.md`. |
| 4 | Single-Tool Bot | 2026-08-20 | 3/5 | Tool_use loop (stop_reason, stateless second call, ** unpacking), first hybrid-workflow project. Folder named `Project4_Single_Tool_Bot` (deviation from numbering convention, intentional). Confirmed "2+2" triggers the calculator tool. Full notes in `Project4_Single_Tool_Bot/PROGRESS.md`. |

## Concepts I still find shaky
- Environment variable lookup order beyond a single simple `.env` file.
- Full range of Claude API error types beyond 400 (credit) / 401 (auth) — e.g. rate limits, overloaded errors.
- Git commit hygiene — running `git status` before committing (mostly fixed in Project 4, keep watching).
- Deeper coding/API fluency generally lighter going forward — will need dedicated review before the exam.

## Next session plan
- Kick off Tier 2, Project 5: Multi-Tool CLI Assistant (several tools, Claude choosing which to use, retries/error handling, agent loop concept) — continuing the hybrid workflow.
