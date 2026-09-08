# Project 10 — Multi-Agent Orchestration — Progress Notes

**Status:** core pipeline complete — `rag_core.py` → three domain
subagents → `orchestrator.py` → `main.py` all built and verified end to
end against all three real documents, plus a working `/ask-network` slash
command and a passing 4-test unit suite. This project used a one-off
"guide-only" workflow exception (scaffolding/guidance while the user wrote
the code themselves) instead of the standing "Claude writes by default"
workflow — see `chat-logs/2026-09-07_1330.md`.

## What got built

- `rag_core.py` — OCR-or-plain extraction (auto-detected per document),
  structure-agnostic fixed-window chunking (1200 chars / 300 overlap),
  embedding (`all-MiniLM-L6-v2`), cosine-similarity retrieval, and grounded
  answering via `claude-haiku-4-5` — generalized from Project 8 to serve
  three independent documents/indexes instead of one.
- `subagents/dwdm_osnr.py`, `ethernet.py`, `ip.py` — thin per-domain
  wrappers, each its own `INDEX_DIR` + `SYSTEM_PROMPT`.
- `orchestrator.py` — `classify_domain()` (Claude-based routing) +
  `route()` (dispatch + full execution trace: domain, source PDF, pages
  referenced, answer).
- `main.py` — interactive CLI loop, one independent `route()` call per
  question.
- `.claude/commands/ask-network.md` — slash command wrapping the
  orchestrator with pre-flight checks (`.env`, all three indexes present)
  and verbatim trace output; mirrored at the repo root so Claude Code
  (which only reads commands from the repo root, not project subfolders)
  actually picks it up.
- 4 unit tests across `test_rag_core.py`, `test_orchestrator.py`,
  `test_subagents.py`.

## Real bugs caught during the build (not hypothetical)

- **`dwdm_osnr.pdf` has the same vector-graphics-text problem as Project
  8's `osnr.pdf`** — confirmed byte-for-byte identical (same MD5), not
  just similar. Reused the OCR pivot from Project 8 rather than
  rediscovering it.
- **Chunk-boundary truncation:** initial 800-char/150-overlap chunking
  looked fine on retrieval previews, but the `ip` subagent's own answer
  said the excerpt was "cut off" — the router-definition sentence
  straddled a chunk boundary. Fixed by widening to 1200/300 and
  rebuilding all three indexes (re-chunk + re-embed only, no OCR redo);
  `dwdm_osnr`'s answers *also* improved as a side effect, confirming the
  wider window was a net gain, not a narrow fix.
- **A misleading "weak retrieval" false alarm:** `ip`'s top hits for
  "What does a router do?" looked weak in a 150-char preview; the real
  answer chunk was already in the top-4, just past the preview cutoff.
  Caught by checking the full `k=16` ranking before concluding retrieval
  itself was broken.
- **Two small paste-error bugs** while assembling `rag_core.py`: a missing
  `import json` and a leftover duplicate `import fitz` alongside the newer
  `import pymupdf as fitz`.
- **A stale progress note:** an earlier session log claimed the three test
  files were still empty stubs; they weren't — they already had complete,
  real tests. Caught before it caused wasted rewrite work.
- **`pytest` needs `-m`:** bare `pytest tests/ -v` failed with
  `ModuleNotFoundError: No module named 'src'` — the console-script entry
  point doesn't add the project root to `sys.path`; `python -m pytest`
  does. All 4 tests pass with the correct invocation.
- **`requirements.txt` corruption:** found saved as UTF-16 with two stray
  shell-command lines (`pip install pytest`, `pytest tests/ -v`) appended
  to the end of the dependency list. Re-saved as plain ASCII, stray lines
  removed, `pytest`/`iniconfig`/`pluggy` added properly as pinned
  dependencies.

## Design decisions made along the way (not specified upstream)

- **Structure-agnostic chunker over heading regex:** checked all three
  real documents' structure before choosing — `osnr.pdf`-style numbered
  headings don't exist in `ethernet.pdf` (prose headings) or `IP.pdf`
  (one slide title per page), so Project 8's heading-based chunker would
  have silently broken on two of three documents.
- **OCR heuristic is per-page, not per-document average:** fraction of
  near-empty *pages* correctly separates `dwdm_osnr.pdf`'s real failure
  (33/40 empty pages) from `IP.pdf`'s genuine sparseness (0/38 empty
  pages, just a low average) — an average-chars-per-page heuristic would
  have conflated the two.
- **`pytesseract` pointed at Tesseract's default Windows install path**
  directly in code, rather than fighting `PATH` resolution after a fresh
  install didn't pick it up.
- **`ask-network.md` lives at the repo root**, not only inside this
  project's own `.claude/commands/` — VS Code's Claude Code reads slash
  commands from the repo root only, so a project-nested copy alone is
  invisible to it.

## Open items

- No conceptual close-out check done yet, so no confidence rating
  recorded in the root `PROGRESS.md`'s Completed Projects table for this
  project.
- No committed script builds the three indexes from scratch (see
  `README.md` Setup step 5) — currently a manual one-off.
- Git commit + push still pending (covers `ask-network.md`, the
  `requirements.txt` fix, and this README/PROGRESS write-up).
- `PLAN.md`'s "also covers" items for this project — Routines/scheduled
  prompts and headless mode — not yet reached.

Full session transcripts: see `chat-logs/`.
