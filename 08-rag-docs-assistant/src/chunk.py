"""Raw (OCR'd) text -> list of {section, chapter, heading, text, pages}.

Splits on the document's own numbered section headings (e.g. "1.3.2 Noise
Figure") rather than a fixed character count, so each chunk is one complete
subsection -- tables and equations stay attached to the paragraph they
belong to, since everything between one heading and the next becomes a
single chunk.

The heading regex is more tolerant than a plain `^\\d+(\\.\\d+)*\\s+\\S` because
extract.py's OCR pass doesn't read every heading line cleanly. Spot-checking
the real document turned up three concrete artifacts this accounts for:
  - a stray leading character before the number, e.g. "- 1.2 Physics..."
    or ". 2.2 EDFA..." (a bullet/marker Tesseract misreads)
  - the document's own duplicated-heading artifact: the exact same
    section+heading appearing twice back-to-back (noted in the source
    spec, confirmed in OCR output) -- sometimes with a line or two of
    body text duplicated right along with it, e.g. Section 6.5.2's
    heading *and* its opening sentence both appear twice in a row before
    the real content continues
  - a heading losing its leading chapter digit entirely, e.g. "1.2.3"
    read as ".2.3" -- recovered using the chapter number of whichever
    real heading was seen most recently
"""

import re

# A heading line, tolerant of a stray leading character (dash/bullet/
# asterisk, or a period specifically followed by whitespace) that OCR
# sometimes inserts before the number. The period case requires a space
# before the digits so it can't collide with MISSING_DIGIT_RE below, where
# the period sits directly against the digits with no space at all. The
# title is required to start with a capital letter -- this is what keeps
# numeric table rows (e.g. "20-40 dB Maximum...") from matching.
HEADING_RE = re.compile(r"^(?:[-•*]\s*|\.\s+)?(\d+(?:\.\d+)*)\s+([A-Z].*\S)\s*$")

# A heading that lost its leading chapter digit (e.g. "1.2.3" -> ".2.3").
# Recovered by prepending the last real chapter number seen.
MISSING_DIGIT_RE = re.compile(r"^\.(\d+(?:\.\d+)+)\s+([A-Z].*\S)\s*$")


def chunk_pages(pages: list[dict]) -> list[dict]:
    """Split page text into chunks along the document's numbered headings.

    `pages` is extract.extract_pages()'s output: a list of
    {"page": int, "text": str}, in page order.

    Returns a list of {"section", "chapter", "heading", "text", "pages"}
    dicts, one per section, in document order. "pages" is a [start, end]
    pair covering every page the section's content touched. Text appearing
    before the first heading (e.g. a title page) is discarded.
    """
    chunks = []
    current = None
    last_chapter = None

    for page in pages:
        page_num = page["page"]
        for raw_line in page["text"].splitlines():
            line = raw_line.strip()
            if not line:
                continue

            section = heading = None
            m = HEADING_RE.match(line)
            if m:
                section, heading = m.group(1), m.group(2)
            else:
                m2 = MISSING_DIGIT_RE.match(line)
                if m2 and last_chapter:
                    section = f"{last_chapter}.{m2.group(1)}"
                    heading = m2.group(2)

            if section:
                # Collapse the document's duplicated-heading artifact: the
                # exact same section+heading appearing again shortly after
                # itself, with no *other* heading in between. Sometimes
                # only the heading line repeats; sometimes a line or two
                # of body text got duplicated right along with it (e.g.
                # Section 6.5.2 in the real document). Either way, this is
                # the same section restarting, not a new one -- discard
                # whatever was accumulated under the first occurrence and
                # keep going from here, rather than keeping a near-empty
                # "stub" chunk alongside the real one.
                if (
                    current
                    and current["section"] == section
                    and current["heading"] == heading
                ):
                    current["lines"] = []
                    current["end_page"] = page_num
                    continue

                if current:
                    chunks.append(_finalize(current))
                current = _start_chunk(section, heading, page_num)
                last_chapter = current["chapter"]
                continue

            if current:
                current["lines"].append(line)
                current["end_page"] = page_num
            # else: text before the first heading -- discarded.

    if current:
        chunks.append(_finalize(current))

    return chunks


def _start_chunk(section: str, heading: str, page: int) -> dict:
    return {
        "section": section,
        "chapter": section.split(".")[0],
        "heading": heading,
        "lines": [],
        "start_page": page,
        "end_page": page,
    }


def _finalize(c: dict) -> dict:
    return {
        "section": c["section"],
        "chapter": c["chapter"],
        "heading": c["heading"],
        "text": "\n".join(c["lines"]).strip(),
        "pages": [c["start_page"], c["end_page"]],
    }


if __name__ == "__main__":
    # Manual sanity check against the real document: run
    # `python src/chunk.py` from the project root and eyeball the section
    # list -- numbering should run cleanly (1.1, 1.1.1, ... 6.x), no
    # obviously-wrong headings, no suspiciously huge or tiny chunks.
    from extract import extract_pages

    pages = extract_pages("docs/osnr.pdf")
    chunks = chunk_pages(pages)

    print(f"{len(chunks)} chunks from {len(pages)} pages\n")
    for c in chunks:
        preview = c["text"][:60].replace("\n", " ")
        print(
            f"[{c['section']:>7}] {c['heading']:<45} "
            f"pages {c['pages']}  ({len(c['text'])} chars)  {preview!r}"
        )
