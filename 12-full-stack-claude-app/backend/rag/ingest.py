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
from sentence_transformers import SentenceTransformer

import db
from rag.rag_core import extract_pages, chunk_text

MODEL_NAME = "all-MiniLM-L6-v2"

_model = None  # loaded once per process, on first use


def embed_text(text: str) -> list[float]:
    """Turn a string into an embedding vector using a local sentence-transformers model."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model.encode(text).tolist()


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
                embedding = embed_text(chunk["text"])
                start_page = chunk["pages"][0]
                cur.execute(
                    """
                    INSERT INTO chunks (document_id, page_number, chunk_text, embedding)
                    VALUES (%s, %s, %s, %s);
                    """,
                    (document_id, start_page, chunk["text"], Json(embedding)),
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
