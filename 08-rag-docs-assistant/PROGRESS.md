# Project 8 — RAG Docs Assistant — Progress Notes

**Finished:** 2026-08-25
**Confidence:** conceptual close-out done separately by the user (not
recorded in this session's transcript) — see the root `PROGRESS.md` for
the standing confidence-tracking format.

## What I built

A command-line assistant that answers questions using only `docs/osnr.pdf`
(a 6-chapter technical document on optical amplifiers/optical networking)
— never Claude's general knowledge — and cites which section each answer
came from. Two-script pipeline: `build_index.py` (slow, one-time: OCR →
chunk by heading → embed → save) and `ask.py` (fast, repeated: retrieve
top-k chunks → grounded, cited Claude answer). Retrieval is plain in-memory
cosine similarity over locally-computed `sentence-transformers` embeddings
— no vector database, appropriate at this document's scale (97 chunks).

## What I learned

- The four-stage RAG shape (chunk → embed → retrieve → generate) and why
  each stage is a genuinely separate concern, not just organizational —
  chunking is a document-structure problem, retrieval is a search problem,
  grounding is a prompting problem.
- **A tool completing without an error says nothing about whether its
  output is correct.** `pypdf` ran cleanly and returned real-looking text
  while recovering under 10% of the document's actual content — only
  caught by cross-checking against two other libraries and then literally
  rendering a page to look at it directly.
- Grounding-via-system-prompt vs. grounding-via-similarity-threshold are
  meaningfully different designs: retrieval always returns *some* ranked
  chunks, even for a wildly off-topic question — it's the generation
  step's own judgment, not a numeric cutoff, that has to recognize when
  the retrieved excerpts don't actually answer the question.
- Hand-crafted unit tests validate understanding of a problem; they don't
  validate that understanding against messy reality. 14/14 synthetic tests
  passed for `chunk.py` and still missed two real bugs that only surfaced
  against the actual OCR'd document.

## Workflow notes — two real deviations from the spec, both flagged and resolved live

1. **Extraction pivoted from `pypdf` to local OCR** (PyMuPDF + Tesseract)
   after discovering the source PDF has most of its body text embedded as
   vector graphics rather than real selectable characters — confirmed
   independently with three extraction libraries before touching any code.
   User was offered a paid Claude-vision-transcription option first, chose
   it, then explicitly overrode that choice one tool call later once the
   cost implication was concrete, landing on local Tesseract OCR instead.
   Recovered ~11x more text (68,715 vs. 6,415 characters); Section 1.3.2 —
   the spec's own key verification example — went from completely missing
   to fully present and correctly cited.
2. **PLAN.md's optional "package as a reusable skill" add-on was included
   this round** (user's choice at planning time) — a project-scoped
   `.claude/skills/ask-osnr-docs/SKILL.md`, drafted by the user
   independently and then reviewed: found and fixed a double-nested file
   path, a stale dependency list, a missing Tesseract prerequisite, and a
   stale citation-format example.

## Pitfalls / open items

- OCR isn't perfect: bullet characters occasionally read as `e`/`�`, a few
  subscripts lose formatting, one real heading lost a leading digit
  (`chunk.py` recovers it from context; not every possible misread is
  covered).
- 22 of 119 chunks (parent headings with no intro text of their own) are
  dropped before embedding — real document structure, not a bug, but
  worth remembering if chunk counts ever look off during debugging.
- Requires Tesseract OCR installed as a system binary to *build* the
  index — a real setup step beyond `pip install`, documented in the
  skill and the README.

## Still a bit shaky

- Nothing project-specific flagged in this session — see the root
  `PROGRESS.md`'s "Concepts I still find shaky" list.

Full session transcripts: `chat-logs/2026-08-24_1043.md` and
`chat-logs/2026-08-25_1114.md`.
