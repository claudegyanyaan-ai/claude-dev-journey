# Project 3 — Structured Data Extractor — Progress Notes

**Finished:** 2026-08-19
**Confidence (1–5):** 3/5

## What I built
A command-line tool (`src/main.py`) that takes messy text describing items
with quantities/prices and uses the Claude API with a system prompt to
extract it into validated JSON.

## What I learned
- The `system` parameter vs. the `messages` list: system holds standing
  instructions that apply to every call; messages holds the actual
  per-call input.
- Why constraining output format in the system prompt (e.g. "respond with
  ONLY JSON, no extra text") matters for code that has to automatically
  parse the response.
- Validating a model's output with `json.loads()` wrapped in `try`/`except
  json.JSONDecodeError` before trusting it — models can occasionally not
  follow instructions perfectly.
- Testing a pure function directly (`parse_response()`) with both valid
  and deliberately-broken input, no API call or file I/O needed for the
  test itself.

## Workflow pivot (important context for future projects)
Mid-project, realized my actual goal is learning to direct Claude Code
effectively, not deep coding fluency for its own sake. After checking what
the real CCDV-F exam tests (API/coding integration is the largest domain,
Claude Code itself is small), agreed on a **hybrid path**: keep the
certification as the goal, but future projects shift toward Project 2's
lighter-touch style (spec → review diff → test) even for new material,
typing less code by hand. Known tradeoff: will need dedicated extra
practice in coding-heavy domains before booking the actual exam.

## Pitfalls I actually hit
- Confused a system prompt with a user prompt on the first attempt —
  mixed the fixed instruction and the one-off input text together.
- Wrote `"content": text` incorrectly as a literal string
  (`"content set to the text argument"`) instead of the actual variable
  reference — a real beginner trap: quotes turn a variable into literal text.
- `messages=` needs to be a list even for one message — passed a bare
  dict once by mistake.
- `README.md` silently bundled into the `test:` commit (again — same
  pattern as Project 2) because `git status` wasn't checked before
  committing.
- A duplicated command block (`git add .` / `commit` / venv setup / pip
  install) got submitted twice by accident — harmless here since venv
  creation just failed safely the second time, but worth noticing.

## Still a bit shaky
- Deeper coding/API fluency in general — intentionally lighter going
  forward per the workflow pivot; will need focused review before the exam.
- Actually running `git status` before every commit, not just after
  something looks wrong.

Full session transcript: see `chat-logs/` in this project.
