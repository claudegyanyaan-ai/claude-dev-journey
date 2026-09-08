# Project 10 — Multi-Agent Orchestration

A networking Q&A system built around the orchestrator/subagent pattern:
Claude itself classifies a question into one of three domains and routes
it to a matching specialist subagent, each doing full RAG retrieval
against its own real document in its own isolated context — no shared
conversation history between the classifier and a subagent, or between
subagents.

## What it does

- **`src/rag_core.py`** — shared extract → chunk → embed → retrieve →
  answer pipeline, generalized from Project 8 so all three subagents reuse
  the same code against their own document and index directory instead of
  three copies of the same logic. Auto-detects whether a document needs
  OCR (`needs_ocr()`) or plain text extraction, and chunks with a
  structure-agnostic fixed-size overlapping window rather than assuming
  any particular heading convention.
- **`src/subagents/dwdm_osnr.py`**, **`ethernet.py`**, **`ip.py`** — three
  thin domain subagents. Each is just its own `INDEX_DIR`, its own
  domain-scoped `SYSTEM_PROMPT`, and a call into `rag_core.answer_from_index()`.
- **`src/orchestrator.py`** — `classify_domain()` asks Claude
  (`claude-haiku-4-5`) which of the three domains a question belongs to —
  a real agentic routing decision, not keyword matching. `route()`
  dispatches to the matching subagent and returns a full trace: domain,
  source PDF, exact pages referenced, and the answer.
- **`src/main.py`** — an interactive CLI loop over `route()`. Each
  question is a fresh, independent call; nothing persists across
  questions or between subagents by design.
- **`.claude/commands/ask-network.md`** (also at the repo root, so Claude
  Code picks it up) — a `/ask-network <question>` slash command that
  pre-flight-checks the environment and runs the orchestrator, printing
  its output verbatim.

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
3. Copy `.env.example` to `.env` and add your `ANTHROPIC_API_KEY`.
4. Install Tesseract OCR (system binary, not a pip package) — needed
   because `docs/dwdm_osnr/dwdm_osnr.pdf`'s text is embedded as vector
   graphics, not real characters. On Windows, the UB Mannheim build; if
   `tesseract` isn't on `PATH` afterward, `rag_core.py` already falls back
   to `C:\Program Files\Tesseract-OCR\tesseract.exe`.
5. Build the three indexes. There's no committed build script yet — run
   this once (save it as a `.py` file and run it; don't paste multi-line
   Python into PowerShell):
   ```python
   from src.rag_core import build_index

   build_index("docs/dwdm_osnr/dwdm_osnr.pdf", "data/index/dwdm_osnr")
   build_index("docs/ethernet/ethernet.pdf", "data/index/ethernet")
   build_index("docs/ip/IP.pdf", "data/index/ip")
   ```
   `data/index/` is gitignored — re-run whichever line's source PDF
   changes.

## Usage

```bash
# One-shot question through the orchestrator
python -m src.orchestrator "What is noise figure in an EDFA?"

# Interactive multi-question loop
python -m src.main
```

Or, from Claude Code, the `/ask-network` slash command:
```
/ask-network What is noise figure in an EDFA?
```

Example output:
```
[orchestrator routed to subagent: dwdm_osnr]
[document: docs/dwdm_osnr/dwdm_osnr.pdf]
[pages referenced: [[10, 11], [8, 9], [10, 10], [7, 8]]]

# Noise Figure in an EDFA
...
```

## How it works

1. `rag_core.needs_ocr()` looks at the *fraction of near-empty pages*
   (not average characters per page) to decide OCR vs. plain extraction —
   an average would have conflated `IP.pdf`'s genuinely sparse-but-real
   text with `dwdm_osnr.pdf`'s real extraction failure. `extract_pages()`
   branches accordingly; `chunk_text()` splits into fixed 1200-character
   windows with 300-character overlap, tracking each chunk's page range
   for citation. `build_index()` / `retrieve()` / `answer_from_index()`
   generalize Project 8's single-document pipeline into a
   `(pdf_path, index_dir)`-parameterized version shared by all three
   subagents.
2. Each subagent wires its own `INDEX_DIR` and `SYSTEM_PROMPT` into the
   shared `answer_from_index()`, which retrieves the top-k chunks and asks
   Claude to answer using *only* those excerpts — refusing rather than
   guessing if they're insufficient.
3. `orchestrator.classify_domain()` sends the question to Haiku with a
   system prompt describing the three domains and asks for one bare
   domain-name word back; anything else raises rather than guessing which
   subagent to use. `route()` dispatches to that subagent and assembles
   the trace directly from the code's own execution (page numbers from
   `retrieve()`'s own chunk metadata) — not from Claude's self-report of
   what it did.
4. `main.py` calls `route()` once per question with no shared state across
   calls — the actual "session/context management across agents" concept
   this project targets: one polluted or leaked context can't affect a
   later question or a different subagent.

## Known limitations

- No committed script builds the three indexes from scratch (see Setup
  step 5) — they were created with one-off calls, not a saved
  `build_indexes.py`.
- Single-turn RAG only — no conversation memory between questions or
  within a subagent call, by design.
- `classify_domain()` has no fallback: if Haiku returns anything other
  than one of the three expected domain words, `route()` raises instead of
  guessing or retrying.
- `k=4` (top-4 chunks retrieved per question) is a fixed default in
  `rag_core.answer_from_index()`, not currently configurable per subagent.

## Tests

```bash
python -m pytest tests/ -v
```
(Bare `pytest tests/ -v` fails with `ModuleNotFoundError: No module named
'src'` — the console-script entry point doesn't add the project root to
`sys.path`; `python -m pytest` does.)

4 tests: `chunk_text()`'s single-chunk and overlap-boundary behavior,
`classify_domain()` with the Anthropic client mocked (no real API call),
and the `ethernet` subagent wiring its own `INDEX_DIR`/`SYSTEM_PROMPT`
into the shared `answer_from_index()` correctly.
