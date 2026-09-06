# Project 9 — Guardrailed Automation Agent — Progress Notes

**Status:** core pipeline complete — `extract.py` → `guardrail.py` →
`store.py` → `agent.py` all built, unit-tested, and verified end-to-end on
the real sample emails and a real (non-sandbox) API key.

## What got built

- `extract.py` — Claude-backed extraction of the 5 lead fields, verbatim
  only, empty string for anything not literally stated.
- `guardrail.py` — pure auto-write/needs-confirmation decision logic:
  completeness, age plausibility, email shape, and a duplicate-email check
  that takes existing rows as a plain argument rather than reading the
  spreadsheet itself.
- `store.py` — safe append-only Excel read/write for
  `data/enrollments.xlsx`.
- `agent.py` — the CLI: extract → decide → auto-write or ask `[y/N]` →
  report a summary, across one or more email files.
- 39 unit tests across 4 test files (`test_extract.py`, `test_guardrail.py`,
  `test_store.py`, `test_agent.py`).

## Real bugs caught during the build (not hypothetical)

- **Markdown-fence non-compliance:** the system prompt told Claude not to
  wrap its JSON in ` ```json ` fences; it did anyway on 2 of the 3 real
  sample emails. Fixed by stripping a leading/trailing fence defensively in
  `parse_response()` before `json.loads()`, rather than fighting the model
  for 100% prompt compliance.
- **Windows file-lock in `store.py`'s tests:** `openpyxl`'s
  `read_only=True` mode keeps a zip file handle open until closed
  explicitly. Harmless on Linux; on Windows it left temp files locked,
  making `tempfile.TemporaryDirectory()` cleanup fail with
  `PermissionError` — invisible on the Linux side of the build, only
  surfaced once the user ran the suite on their actual Windows machine.
  Fixed with explicit `wb.close()` in both `load_rows()` and `append_row()`.
- **Excel-open `PermissionError` on a real run:** `agent.py`'s first live
  end-to-end run failed writing to `enrollments.xlsx` because the user had
  it open in Excel at the time — not a code bug, but real, expected OS-level
  file locking. Worth knowing as a usage note, not something `store.py`
  should (or safely can) work around.
- **A fake `401 Unauthorized`:** debugging the API key looked at first like
  an invalid/revoked key, several checks deep (console verification,
  billing, byte-for-byte key comparison across re-pastes) before the real
  cause surfaced — a network proxy in one sandboxed shell was intercepting
  the request and returning its own plain-text 401 before it ever reached
  Anthropic's servers (Anthropic's real auth errors are JSON with a
  `type: authentication_error` body; this wasn't). The key, billing, and
  console setup were fine the whole time.

## Design decisions made along the way (not specified upstream)

- Age plausibility bounds: 10–100 (`guardrail.MIN_PLAUSIBLE_AGE`/
  `MAX_PLAUSIBLE_AGE`) — a judgment call, easy to change.
- Spreadsheet location/schema: `data/enrollments.xlsx`, one `"Enrollments"`
  sheet, columns in `guardrail.FIELDS` order — nothing existed yet and
  nothing upstream pinned this down, so `store.py` picked reasonable
  defaults rather than blocking on it.
- `agent.py` defaults its confirmation prompt to **No** on a blank answer
  or EOF — consistent with the project's "never act on an uncertain case"
  discipline threaded through extract/guardrail/store.

## Open items

- README/PROGRESS.md/chat-log write-up done; git commit still pending as
  of this note (commands handed to the user directly rather than run on
  their behalf).
- No conceptual close-out check done yet, so no confidence rating recorded
  in the root `PROGRESS.md`'s Completed Projects table for this project.
- No live-inbox integration — sample `.txt` files only, by design.

Full session transcript: see `chat-logs/`.
