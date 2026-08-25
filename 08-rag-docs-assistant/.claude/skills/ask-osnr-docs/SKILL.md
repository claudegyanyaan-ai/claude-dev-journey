---
name: ask-osnr-docs
description: Answer questions about docs/osnr.pdf (a 6-chapter technical document on optical amplifiers and optical networking — noise figure, OSNR, gain, EDFAs, etc.) using this project's local RAG pipeline, with every answer grounded in and citing the actual section it came from. Use when the user asks a question about optical amplifiers, noise figure, OSNR, or any topic that might be in osnr.pdf, or asks to "query the docs", "search the document", "look this up in osnr.pdf". Also covers rebuilding the index after the PDF changes, and diagnosing bad answers (retrieval vs. generation).
allowed-tools: Bash
---

# Ask osnr.pdf (RAG pipeline)

This project (`08-rag-docs-assistant`) answers questions using *only*
`docs/osnr.pdf` — never Claude's general knowledge — and cites the section
each answer came from. The pipeline is two separate scripts: a slow,
one-time indexing step and a fast, repeated querying step. Don't
re-derive this from scratch each session — follow the procedure below.

## Before answering a question

Run these from the `08-rag-docs-assistant/` project folder (not the repo
root).

1. **Activate the project's virtualenv** — dependencies (anthropic,
   sentence-transformers, numpy, pymupdf, pytesseract, python-dotenv) live
   there, not globally.
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
2. **Confirm Tesseract OCR is installed as a system binary** — required
   for `build_index.py` (extraction is OCR-based, not text-layer
   extraction; see "Why OCR, not pypdf" below). Check with
   `tesseract --version`; if that fails, install it
   (`winget install UB-Mannheim.TesseractOCR` on Windows) before rebuilding
   the index. Not needed just to run `ask.py`/`retrieve.py` against an
   already-built index.
3. **Confirm `ANTHROPIC_API_KEY` is set** — copy `.env.example` to `.env`
   and fill it in if `.env` doesn't exist yet.
4. **Check whether an index already exists**: look for
   `data/index/chunks.json`, `embeddings.npy`, and `meta.json`. If any are
   missing, or `docs/osnr.pdf` has changed since the index was built, run
   the one-time indexing step first:
   ```
   python src/build_index.py
   ```
   Takes roughly 60–90s (OCR is the slow part). Rebuilds all three files
   under `data/index/`. Skip this step if a valid index is already there —
   don't rebuild it on every question.
5. **Answer the question**:
   ```
   python src/ask.py "the user's question"
   ```
   Prints a grounded answer followed by a `Source: Section X.Y - Heading`
   line. If the excerpts retrieved don't actually cover the question, the
   answer will say so plainly instead of falling back to general
   knowledge — that is correct, expected behavior, not a bug to fix.

## Design constraints to preserve

These were deliberate choices made for this project specifically — don't
silently swap them out for something "better" without flagging it first:

- **Retrieval is in-memory cosine similarity** over locally-computed
  `sentence-transformers` (`all-MiniLM-L6-v2`) embeddings — no vector
  database. Fine at this document's scale (well under 100 chunks).
- **Chunks are split on the document's own numbered section headings**
  (`chunk.py`), not fixed-size blocks — keeps tables/equations attached
  to their explanation. Don't switch to naive character-count chunking.
- **Grounding is enforced by `ask.py`'s system prompt**, not a similarity
  score cutoff. Retrieval always returns `k` chunks (default 4) even for
  a completely unrelated question — cosine similarity always produces
  *some* ranking. It's Claude's own judgment, guided by the prompt, that
  recognizes when the retrieved excerpts don't actually answer the
  question and says so.
- **Indexing and querying stay separate scripts** — never merge
  `build_index.py`'s slow, one-time work into the fast, per-question path
  in `ask.py`.
- **Extraction is OCR (`extract.py`, via PyMuPDF + Tesseract), not
  `pypdf` text-layer extraction.** This isn't the original design — it was
  discovered mid-project that `docs/osnr.pdf` has most of its body text
  embedded as vector graphics rather than real selectable characters.
  Confirmed independently with three text-extraction libraries (`pypdf`,
  `pdfplumber`, `PyMuPDF`), all of which recovered well under 10% of the
  document's actual content, missing Section 1.3.2 entirely. OCR recovers
  ~11x more text (68,715 vs. 6,415 characters) and is what makes this
  pipeline actually work. Don't "simplify" this back to plain `pypdf`
  extraction — it would silently gut the index.

## Diagnosing a bad answer

If an answer looks wrong or under-cited, isolate *where* the problem is
before touching any code:

```
python src/retrieve.py "the same question"
```

This runs retrieval only (no call to Claude) and prints the top-k chunks
with their similarity scores and a text preview. If the right section
isn't in that list, it's a retrieval/chunking problem (`chunk.py`,
embedding text). If the right section *is* in that list but `ask.py`'s
answer is still wrong, it's a generation/prompting problem (`ask.py`'s
`SYSTEM_PROMPT`).

## Known limitations

- One document, one index — no multi-document support.
- No conversation memory — every question is answered independently of
  prior ones.
- If `data/index/` is missing entirely, `ask.py` fails with a clear
  message pointing at `build_index.py` rather than a raw traceback.