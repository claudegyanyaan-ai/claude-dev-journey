"""Embed chunks and load documents into Postgres.

embed_text() turns a string into a vector using a local sentence-transformers
model (no API call, no cost -- same embedding model used in Projects 8/10).
ingest_document() runs one PDF through rag_core's extract -> chunk pipeline,
embeds every chunk, and writes the result into the documents/chunks tables
defined in db.py.
"""

import sys
from pathlib import Path

# db.py lives one directory up (backend/); this file lives in backend/rag/.
sys.path.append(str(Path(__file__).resolve().parent.parent))

from psycopg2.extras import Json

import db
from rag.rag_core import extract_pages, chunk_text

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None  # loaded once per process, on first use


def embed_text(text: str) -> list[float]:
    """Turn a string into an embedding vector using a local sentence-transformers model.

    The sentence_transformers import lives inside this function, not at
    module level -- importing it (and its dependency, torch) costs several
    hundred MB of RAM just from the import itself, before any model is
    even loaded. On a memory-constrained deploy (Render's free/starter
    tiers), that import happening at process startup -- triggered merely
    by main.py's import chain reaching this module -- was enough by
    itself to OOM-kill the process before uvicorn ever bound to a port.
    Deferring the import to first actual use means the server starts
    and binds its port immediately; the memory cost only lands on
    whichever request first calls this function (the first /ask or
    /upload), not on every process startup.
    """
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model.encode(text).tolist()


def _clean_text(text: str) -> str:
    """Strip NUL (0x00) bytes from extracted PDF text.

    Some PDFs (depending on their font/encoding) yield extracted text
    with embedded NUL bytes. Postgres text columns cannot store NUL
    bytes at all -- it's a hard limitation of Postgres itself, not
    anything specific to this schema -- so an uncleaned chunk crashes
    the INSERT with "A string literal cannot contain NUL (0x00)
    characters." Stripping it here is harmless: NUL isn't a printable
    character that could appear in real document content anyway.
    """
    return text.replace("\x00", "")


def ingest_document(pdf_path: str, topic: str, filename: str) -> int:
    """Extract, chunk, embed, and store one PDF's content in Postgres.

    Inserts one row into documents (topic, filename), then one row per
    chunk into chunks (document_id, page_number, chunk_text, embedding).
    Everything for this document runs inside a single transaction, so a
    failure partway through (a bad chunk, a dropped DB connection) rolls
    back the whole document instead of leaving it half-written.

    Returns the number of chunks inserted.
    """
    pages = extract_pages(pdf_path)
    chunks = chunk_text(pages)

    conn = db.get_conn()
    with conn:  # commits if the block exits cleanly, rolls back on exception
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (topic, filename) VALUES (%s, %s) RETURNING id;",
                (topic, filename),
            )
            document_id = cur.fetchone()[0]

            for chunk in chunks:
                clean_text = _clean_text(chunk["text"])
                embedding = embed_text(clean_text)
                start_page = chunk["pages"][0]
                cur.execute(
                    """
                    INSERT INTO chunks (document_id, page_number, chunk_text, embedding)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (document_id, start_page, clean_text, Json(embedding)),
                )

    return len(chunks)


if __name__ == "__main__":
    # Seed the three built-in topics. Run as `python rag/ingest.py` from
    # the backend/ folder (paths below are relative to that).
    seeds = [
        ("docs/dwdm_osnr/dwdm_osnr.pdf", "dwdm_osnr", "dwdm_osnr.pdf"),
        ("docs/ethernet/ethernet.pdf", "ethernet", "ethernet.pdf"),
        ("docs/ip/IP.pdf", "ip", "IP.pdf"),
    ]

    for pdf_path, topic, filename in seeds:
        count = ingest_document(pdf_path, topic, filename)
        print(f"{topic}: inserted {count} chunks from {pdf_path}")
