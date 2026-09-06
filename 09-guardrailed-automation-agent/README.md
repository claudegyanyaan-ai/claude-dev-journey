# Project 9 — Guardrailed Automation Agent

An agent that extracts structured lead data (name, age, course_name,
contact, email) from course-enrollment inquiry emails and appends it to an
Excel enrollment sheet — but pauses for your explicit confirmation whenever
the extracted data looks incomplete, implausible, or already enrolled,
rather than acting on it blindly.

## What it does

- **`src/extract.py`** — sends one email's raw text to Claude and gets back
  the 5 fields as a JSON object. Every value is copied verbatim from the
  email; a field that isn't literally stated comes back as `""`, never a
  guess.
- **`src/guardrail.py`** — pure decision logic, no network or file I/O.
  Given an extracted lead and the list of already-enrolled rows, decides
  `auto_write` or `needs_confirmation`, with a plain-language reason for
  every pause.
- **`src/store.py`** — safe append-only Excel I/O for `data/enrollments.xlsx`.
  Reads every existing row (for the duplicate check) and appends one new
  row; never updates or deletes an existing one.
- **`src/agent.py`** — the CLI that ties the three together for one or more
  email files: extract, decide, auto-write or ask `[y/N]`, report a summary.

## Setup

1. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1      # PowerShell
   # or: source .venv/Scripts/activate   # Windows Git Bash / macOS / Linux
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your `ANTHROPIC_API_KEY` (same
   key/setup as Project 1). Needed for `extract.py` and `agent.py`, not for
   `guardrail.py` or `store.py` alone.

## Usage

```powershell
# Run the full pipeline against one or more sample emails
python src\agent.py data\sample_emails\clean_01.txt

# Multiple files in one run
python src\agent.py data\sample_emails\clean_01.txt data\sample_emails\implausible_age_01.txt

# Run just extraction, no guardrail/store involved
python src\extract.py data\sample_emails\missing_age_01.txt
```

Example `agent.py` output for a clean, first-time lead:
```
=== data\sample_emails\clean_01.txt ===
Extracted:
  name: 'Priya Sharma'
  age: '28'
  course_name: 'Advanced Python for Data Science'
  contact: '98765-43210'
  email: 'priya.sharma88@gmail.com'
-> Auto-written to the enrollment spreadsheet.
```

...and for one that needs a human decision:
```
-> Needs confirmation:
     - duplicate email: already enrolled as 'Priya Sharma'
Write this row anyway? [y/N]:
```

**Close `data/enrollments.xlsx` in Excel before running `agent.py`** — Excel
locks the file while it's open, and `openpyxl` can't write to a locked file
(you'll get a `PermissionError`, not silent data loss).

## How it works

1. `extract.py` sends the email text to Claude (`claude-haiku-4-5`) under a
   system prompt that requires every value to be copied verbatim, never
   inferred. Claude doesn't always honor "no markdown code fences" despite
   being told to — `extract.py` strips a leading/trailing ` ``` ` fence
   defensively before parsing, since fighting the model for 100% prompt
   compliance is more expensive than handling the 2-in-3 case observed in
   testing.
2. `guardrail.py` checks four things independently: all 5 fields present,
   age within a plausible range (10–100 — a judgment call, not something
   pinned down in the original spec; easy to change), email shape via
   regex, and no existing row sharing that email (case-insensitive). Any
   failure adds a reason and flips the decision to `needs_confirmation`;
   all four passing means `auto_write`.
3. `store.py` reads `data/enrollments.xlsx` as a list of dicts and appends
   new rows in a fixed column order (`guardrail.FIELDS`, imported rather
   than redefined, so the two modules can't drift apart). It explicitly
   closes every workbook it opens — `openpyxl`'s `read_only=True` mode
   otherwise leaves a file handle open, which is harmless on Linux but
   silently kept temp files locked on Windows during testing.
4. `agent.py` is the only piece that talks to a human: it prints what was
   extracted, either writes it automatically or shows the guardrail's
   reason(s) and asks `Write this row anyway? [y/N]`, and reports how many
   of the given emails actually got written by the end.

## Known limitations

- One email per file, one lead per email — no batch inbox parsing, no
  multi-lead emails.
- Age plausibility (10–100) and the spreadsheet's location/schema
  (`data/enrollments.xlsx`, one `Enrollments` sheet) were both judgment
  calls made during the build, not specified anywhere upstream — both are
  simple constants (`guardrail.MIN_PLAUSIBLE_AGE`/`MAX_PLAUSIBLE_AGE`,
  `store.DEFAULT_PATH`/`SHEET_NAME`) if either needs to change.
- `store.py` never updates or deletes a row — correcting a bad entry means
  editing the spreadsheet by hand.
- Input is sample `.txt` files, not a live inbox — a Gmail connector is
  available if/when this extends to real mail, deliberately out of scope
  for this build.
- `agent.py`'s confirmation prompt is a blocking terminal `input()` — no
  non-interactive/scripted mode.

## Tests

```bash
python -m unittest discover tests -v
```

39 tests across four files. `test_extract.py` and `test_guardrail.py` cover
pure logic against hand-crafted input (no network, no files). `test_store.py`
does real file I/O but only against `tempfile.TemporaryDirectory()` sheets,
never the real one. `test_agent.py` mocks `extract.extract_from_file` (the
only network call) and drives real `guardrail.py`/`store.py` logic
underneath, including a duplicate-across-runs scenario — same "test pure
logic in isolation, isolate the real I/O" approach as Projects 6 and 8.
