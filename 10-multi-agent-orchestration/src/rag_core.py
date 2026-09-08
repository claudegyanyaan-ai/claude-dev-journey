"""Shared RAG building blocks, reused across all three domain subagents.

Generalizes Project 8's extract -> chunk -> embed -> retrieve pipeline so
each subagent (dwdm_osnr, ethernet, ip) can call the same functions
against its own document and its own index directory, instead of three
copies of the same logic.

Two things are deliberately different from Project 8's version, because
this project has three structurally different documents instead of one:

- extract_pages() auto-detects whether a document needs OCR (dwdm_osnr.pdf,
  which has most of its text embedded as vector graphics) or plain text
  extraction (ethernet.pdf, IP.pdf), via needs_ocr() below, rather than
  assuming every document needs OCR.
- chunk_text() splits by fixed-size overlapping windows rather than by
  matching numbered section headings -- osnr.pdf's "1.3.2 Noise Figure"
  style heading regex doesn't exist in ethernet.pdf (prose headings, no
  numbers) or IP.pdf (one slide title per page), so a structure-agnostic
  chunker is the only one that works uniformly across all three.
"""

import io
import json
import shutil
from pathlib import Path
import anthropic
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
    callers (chunk_text, build_index) don't need to know or care which.
    """
    if needs_ocr(pdf_path):
        return _extract_pages_ocr(pdf_path, dpi=dpi)
    return _extract_pages_plain(pdf_path)


def chunk_text(pages: list[dict], chunk_size: int = 1200, overlap: int = 300) -> list[dict]:
    """Split extracted page text into overlapping fixed-size chunks.

    `pages` is extract_pages()'s output: a list of {"page": int, "text": str},
    in page order. Structure-agnostic on purpose -- unlike a heading-based
    chunker, this doesn't assume numbered sections, prose headings, or
    slide titles, so it works the same way on any of the three documents.

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
    #   python src/rag_core.py docs/ethernet/ethernet.pdf
    # from the project root and eyeball page count, chunk count, and
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
    import json

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
MIN_CHUNK_CHARS = 20  # drop any leftover chunk too short to carry real meaning
ANSWER_MODEL = "claude-haiku-4-5"

_model = None  # loaded lazily, once per process


def _load_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    norms[norms == 0] = 1
    return vectors / norms


def build_index(pdf_path, index_dir) -> None:
    """Extract -> chunk -> embed -> save, for one document into its own index_dir.

    Each subagent calls this once (or whenever its own PDF changes) with
    its own pdf_path and index_dir -- e.g. the ethernet subagent builds
    data/index/ethernet/ from docs/ethernet/ethernet.pdf, independently
    of the other two subagents' indexes.
    """
    index_path = Path(index_dir)
    index_path.mkdir(parents=True, exist_ok=True)

    print(f"1/4  Extracting text from {pdf_path}...")
    pages = extract_pages(pdf_path)
    print(f"     {len(pages)} pages extracted")

    print("2/4  Chunking...")
    chunks = [c for c in chunk_text(pages) if len(c["text"]) >= MIN_CHUNK_CHARS]
    print(f"     {len(chunks)} chunks")

    print(f"3/4  Embedding with {MODEL_NAME}...")
    model = _load_model()
    embeddings = model.encode([c["text"] for c in chunks], show_progress_bar=True)
    embeddings = np.asarray(embeddings, dtype=np.float32)

    print(f"4/4  Saving index to {index_path}/...")
    with open(index_path / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    np.save(index_path / "embeddings.npy", embeddings)
    with open(index_path / "meta.json", "w", encoding="utf-8") as f:
        json.dump(
            {"model": MODEL_NAME, "chunk_count": len(chunks), "source_pdf": str(pdf_path)},
            f, indent=2,
        )
    print(f"Done. {len(chunks)} chunks -> {index_path}/")


def load_index(index_dir) -> dict:
    index_path = Path(index_dir)
    with open(index_path / "chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    embeddings = np.load(index_path / "embeddings.npy")
    return {"chunks": chunks, "embeddings": _normalize(embeddings)}


def retrieve(query: str, index_dir, k: int = 4) -> list[dict]:
    """Return the top-k chunks most similar to `query` from index_dir, most similar first."""
    index = load_index(index_dir)
    model = _load_model()
    query_vec = _normalize(np.asarray(model.encode([query]), dtype=np.float32))[0]
    scores = index["embeddings"] @ query_vec
    top_k_idx = np.argsort(-scores)[:k]
    results = []
    for i in top_k_idx:
        chunk = dict(index["chunks"][i])
        chunk["score"] = float(scores[i])
        results.append(chunk)
    return results

def answer_from_index(query: str, index_dir, system_prompt: str, k: int = 4) -> dict:
    """Retrieve top-k chunks for `query` from index_dir and ask Claude to
    answer using ONLY those excerpts, per system_prompt's rules.

    Returns {"answer": <text>, "pages_referenced": [[start, end], ...]} --
    the page ranges are reported directly from retrieve()'s own chunk
    metadata, not from Claude's self-report, so this is an honest trace of
    which pages actually got sent as context, not just what the model
    claims it used.
    """
    chunks = retrieve(query, index_dir, k=k)
    excerpts = "\n\n".join(
        f"[pages {c['pages'][0]}-{c['pages'][1]}]\n{c['text']}" for c in chunks
    )
    user_message = f"Excerpts:\n\n{excerpts}\n\nQuestion: {query}"

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=ANSWER_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    answer_text = "\n".join(b.text for b in response.content if b.type == "text")
    return {
        "answer": answer_text,
        "pages_referenced": [c["pages"] for c in chunks],
    }
