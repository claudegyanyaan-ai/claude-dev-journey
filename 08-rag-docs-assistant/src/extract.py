"""PDF -> raw text, preserving page numbers.

The source PDF (docs/osnr.pdf) turned out to have most of its body text
embedded as vector graphics rather than real selectable characters --
confirmed by cross-checking three separate text-extraction libraries
(pypdf, pdfplumber, PyMuPDF), all of which recovered well under 10% of the
document's actual content, including missing Section 1.3.2 entirely. So
instead of extracting a text layer that mostly doesn't exist, this module
renders each page to an image and runs local OCR (Tesseract, via
pytesseract) on it. Fully local, no API calls -- same as the pypdf approach
this replaced, just recognizing pixels instead of reading text objects.

Deliberately returns text broken out *per page* rather than one big string:
chunk.py needs to know which page(s) each section came from, and page
boundaries are the only place that information exists.
"""

import io
import shutil
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

# Tesseract isn't reliably on PATH right after a fresh Windows install --
# fall back to the default UB Mannheim install location if `tesseract`
# isn't already resolvable.
if shutil.which("tesseract") is None:
    _default_windows_path = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    if _default_windows_path.exists():
        pytesseract.pytesseract.tesseract_cmd = str(_default_windows_path)


def extract_pages(pdf_path: str | Path, dpi: int = 200) -> list[dict]:
    """OCR a PDF, one entry per page.

    Returns a list of {"page": <1-indexed page number>, "text": <OCR text>},
    in page order. `dpi` controls render resolution before OCR -- 200 is a
    good balance of accuracy vs. speed for this document.
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
                    "Install it (e.g. `winget install UB-Mannheim.TesseractOCR`) "
                    "and make sure tesseract.exe is on PATH or at the default "
                    r"'C:\Program Files\Tesseract-OCR\tesseract.exe' location."
                ) from e
            pages.append({"page": page_number, "text": text})
    finally:
        doc.close()

    return pages


if __name__ == "__main__":
    # Quick manual sanity check: run `python src/extract.py` from the
    # project root and eyeball the output -- page count looks right,
    # headings/text are readable, no obvious garbling.
    import sys
    import time

    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "docs/osnr.pdf"
    start = time.time()
    pages = extract_pages(pdf_path)
    elapsed = time.time() - start

    total_chars = sum(len(p["text"]) for p in pages)
    print(
        f"OCR'd {len(pages)} pages from {pdf_path} "
        f"({total_chars} total chars, {elapsed:.1f}s)\n"
    )
    for p in pages[:3]:
        print(f"--- Page {p['page']} (first 400 chars) ---")
        print(p["text"][:400])
        print()
