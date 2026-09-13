"""Shared RAG building blocks: extract -> chunk.

Relocated from Project 10's src/rag_core.py. needs_ocr(), extract_pages(),
and chunk_text() are unchanged -- same OCR-detection heuristic and same
structure-agnostic overlapping-window chunker, still generalized to work
across dwdm_osnr.pdf (needs OCR), ethernet.pdf, and IP.pdf (plain text)
without assuming any particular heading style.

Everything specific to Project 10's per-domain local index files
(build_index/load_index/retrieve/answer_from_index, the embedding model,
and the Claude-based answering call) has been dropped -- this project
embeds and stores chunks in Postgres instead (see ingest.py), and
retrieval/answering are separate concerns that will live elsewhere in
this backend.
"""

import io
import shutil
from pathlib import Path

import pymupdf as fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pypdf import PdfReader

# Tesseract isn't reliably on PATH right after a fresh Windows install --
# fall back to the default UB Mannheim install location if `tesseract`
# isn't already resolvable. (Same fallback Project 8's extract.py uses.)
if shutil.which("tesseract") is None:
    _default_windows_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if _default_windows_path.exists():
        pytesseract.pytesseract.tesseract_cmd = str(_default_windows_path)

EMPTY_PAGE_CHAR_THRESHOLD = 20
EMPTY_PAGE_RATIO_THRESHOLD = 0.25


def needs_ocr(
    pdf_path,
    empty_page_char_threshold: int = EMPTY_PAGE_CHAR_THRESHOLD,
    empty_page_ratio_threshold: float = EMPTY_PAGE_RATIO_THRESHOLD,
) -> bool:
    """Return True if pdf_path looks like it needs OCR rather than plain text extraction.

    Heuristic: a document where a large fraction of pages come back with
    almost no extractable text is treated as OCR-worthy (this is the
    signature of text embedded as vector graphics, not real characters).
    A document with consistently low-but-present text per page (e.g. a
    sparse slide deck) is not -- an average-chars-per-page threshold would
    conflate the two, but counting near-empty *pages* doesn't, since a
    genuinely sparse document still has some real text on every page.
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    if total_pages == 0:
        return False

    empty_pages = 0
    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        if len(text) < empty_page_char_threshold:
            empty_pages += 1

    return (empty_pages / total_pages) > empty_page_ratio_threshold


def _extract_pages_plain(pdf_path) -> list[dict]:
    """Plain pypdf text extraction, one entry per page."""
    reader = PdfReader(pdf_path)
    return [
        {"page": i + 1, "text": page.extract_text() or ""}
        for i, page in enumerate(reader.pages)
    ]


def _extract_pages_ocr(pdf_path, dpi: int = 200) -> list[dict]:
    """Render each page to an image and OCR it with Tesseract (via pytesseract).

    Same approach as Project 8's extract.py: for a document whose text is
    embedded as vector graphics rather than real characters, there's no
    text layer worth reading -- so recognize pixels instead.
    """
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        raise RuntimeError(f"Could not open PDF at {pdf_path}: {e}") from e

    pages = []
    try:
        for page_number, page in enumerate(doc, start=1):
            pix = page.get_pixmap(dpi=dpi)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
            try:
                text = pytesseract.image_to_string(image)
            except pytesseract.TesseractNotFoundError as e:
                raise RuntimeError(
                    "Tesseract OCR isn't installed or couldn't be found. "
                    "Install it and make sure tesseract.exe is on PATH or "
                    r"at the default 'C:\Program Files\Tesseract-OCR\tesseract.exe' location."
                ) from e
            pages.append({"page": page_number, "text": text})
    finally:
        doc.close()

    return pages


def extract_pages(pdf_path, dpi: int = 200) -> list[dict]:
    """Extract text per page, auto-choosing plain extraction or OCR.

    Returns a list of {"page": <1-indexed page number>, "text": <text>},
    in page order, regardless of which extraction method was used --
    callers (chunk_text, ingest_document) don't need to know or care which.
    """
    if needs_ocr(pdf_path):
        return _extract_pages_ocr(pdf_path, dpi=dpi)
    return _extract_pages_plain(pdf_path)


def chunk_text(pages: list[dict], chunk_size: int = 1200, overlap: int = 300) -> list[dict]:
    """Split extracted page text into overlapping fixed-size chunks.

    `pages` is extract_pages()'s output: a list of {"page": int, "text": str},
    in page order. Structure-agnostic on purpose -- unlike a heading-based
    chunker, this doesn't assume numbered sections, prose headings, or
    slide titles, so it works the same way on any document.

    Returns a list of {"text", "pages"} dicts, in document order. "pages"
    is the [start, end] page range each chunk's characters fall within.
    """
    full_text = ""
    page_spans = []  # (start_offset, end_offset, page_number)
    for p in pages:
        start = len(full_text)
        full_text += p["text"] + "\n"
        page_spans.append((start, len(full_text), p["page"]))

    def pages_for(start_offset, end_offset):
        covered = [pg for (s, e, pg) in page_spans if s < end_offset and e > start_offset]
        return [min(covered), max(covered)] if covered else [1, 1]

    chunks = []
    step = chunk_size - overlap
    for start in range(0, len(full_text), step):
        end = min(start + chunk_size, len(full_text))
        text = full_text[start:end].strip()
        if text:
            chunks.append({"text": text, "pages": pages_for(start, end)})
        if end == len(full_text):
            break

    return chunks


if __name__ == "__main__":
    # Manual sanity check: run
    #   python rag/rag_core.py docs/ethernet/ethernet.pdf
    # from the backend/ folder and eyeball page count, chunk count, and
    # whether the first chunk's text looks sane.
    import sys
    import time

    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "docs/ethernet/ethernet.pdf"

    print(f"needs_ocr({pdf_path}) = {needs_ocr(pdf_path)}")

    start = time.time()
    pages = extract_pages(pdf_path)
    elapsed = time.time() - start
    total_chars = sum(len(p["text"]) for p in pages)
    print(f"extracted {len(pages)} pages, {total_chars} chars, {elapsed:.1f}s")

    chunks = chunk_text(pages)
    print(f"chunked into {len(chunks)} chunks\n")
    print("--- first chunk ---")
    print(f"pages {chunks[0]['pages']}")
    print(chunks[0]["text"][:300])
