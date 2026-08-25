# Project 8 — RAG Docs Assistant

A command-line assistant that answers questions using only `docs/osnr.pdf`
(a 6-chapter technical document on optical amplifiers/optical networking) —
not Claude's general knowledge — and cites which section of the document
each answer came from.

## What it does

- **`src/build_index.py`** — one-time, slow step. OCRs `docs/osnr.pdf`,
  splits it into chunks along the document's own numbered section headings
  (e.g. `1.3.2 Noise Figure`), embeds each chunk locally, and saves the
  result under `data/index/`.
- **`src/ask.py`** — fast, repeated step. Takes a question, retrieves the
  most relevant chunks from the saved index, and asks Claude to answer
  using *only* those excerpts — citing the section(s) it drew from, and
  saying so plainly if the excerpts don't actually cover the question
  rather than falling back to general knowledge.

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
3. Install Tesseract OCR as a **system binary** (not just the pip
   package) — `build_index.py`'s extraction step depends on it:
   ```powershell
   winget install UB-Mannheim.TesseractOCR
   ```
   Verify with `tesseract --version`. Only needed to *build* the index —
   not needed to run `ask.py`/`retrieve.py` against an already-built one.
4. Copy `.env.example` to `.env` and add your `ANTHROPIC_API_KEY` (same
   key/setup as Project 1). Needed for `ask.py`, not for indexing.

## Usage

```powershell
# One-time: build the index from docs/osnr.pdf (~60-90s, OCR is the slow part)
python src/build_index.py

# Ask a question (repeatable, fast)
python src/ask.py "What is the quantum limit for noise figure?"
```

Example output:
```
Based on the excerpts provided, the quantum limit for noise figure is 3 dB.
...
Source: Section 1.3.2 - Noise Figure
```

If the question isn't covered by the document, `ask.py` says so instead of
answering from general knowledge — that's correct, expected behavior.

For diagnosing a specific bad answer, `src/retrieve.py "question"` runs
retrieval only (no call to Claude) and prints the top-k chunks with their
similarity scores — useful for telling a retrieval problem apart from a
generation/prompting one.

## How it works

1. **`extract.py`** — OCR, not text-layer extraction. The source PDF turned
   out to have most of its body text embedded as vector graphics rather
   than real selectable characters (confirmed independently with three
   text-extraction libraries, all of which recovered under 10% of the
   document's actual content). Each page is rendered to an image
   (PyMuPDF) and OCR'd locally (Tesseract, via `pytesseract`) instead —
   fully local, no API cost, ~11x more text recovered than the original
   `pypdf` approach.
2. **`chunk.py`** — splits OCR'd text on the document's own numbered
   section headings, tolerating several real OCR artifacts found while
   testing against the actual document (a stray leading dash/period
   before a heading number, and one heading that lost its leading chapter
   digit entirely) and the document's own duplicated-heading generation
   artifact. Each chunk carries chapter/section/heading/page-range
   metadata — what makes citations possible.
3. **`build_index.py`** — orchestrates extract → chunk → embed
   (`sentence-transformers`, `all-MiniLM-L6-v2`, local) → save. Drops
   near-empty chunks (parent headings with no intro text of their own)
   before embedding.
4. **`retrieve.py`** — in-memory cosine similarity over the saved
   embeddings (no vector database — overkill at this document's scale,
   well under 100 chunks).
5. **`ask.py`** — sends the top-k retrieved chunks to Claude (`claude-haiku-4-5`)
   under a system prompt that enforces grounding and citation. Retrieval
   always returns *some* ranked chunks, even for an unrelated question —
   it's Claude's own judgment, guided by the prompt, that recognizes when
   the excerpts don't actually answer the question.

## Known limitations

- One document, one index — no multi-document support.
- No conversation memory — each question is answered independently.
- OCR isn't perfect: bullet characters occasionally come through as `e`
  or `�`, a few subscripts lose their subscript formatting, and one
  heading in the real document lost a digit (`chunk.py` recovers it from
  context, but not every possible OCR misread is covered).
- Requires Tesseract OCR installed as a system binary to *build* the
  index — not just a pip package, a real setup step (see Setup above).
- If `data/index/` is missing entirely, `ask.py` fails with a clear
  message pointing at `build_index.py` rather than a raw traceback.

## Tests

```bash
python -m unittest discover tests
```

Covers `chunk.py`'s heading-splitting logic against hand-crafted text —
including the OCR-artifact tolerance and duplicate-heading collapsing
found while testing against the real document. No PDF parsing or
embedding model involved, same "test the pure logic separately" approach
as Project 6.
