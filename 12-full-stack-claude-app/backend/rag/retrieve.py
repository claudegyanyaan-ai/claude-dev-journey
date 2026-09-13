"""Search a topic's stored chunks for the ones most relevant to a query.

Reuses ingest.py's embed_text() (and the model instance it lazily loads)
so the query gets embedded with the exact same model/settings the stored
chunks were embedded with, without loading sentence-transformers a second
time in the same process.
"""

import sys
from pathlib import Path

# db.py lives one directory up (backend/); this file lives in backend/rag/.
sys.path.append(str(Path(__file__).resolve().parent.parent))

import numpy as np

import db
from rag.ingest import embed_text


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors: 1.0 = identical direction, 0.0 = unrelated, -1.0 = opposite."""
    a = np.asarray(a)
    b = np.asarray(b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def search_topic(topic: str, query: str, top_k: int = 3) -> list[dict]:
    """Return the top_k chunks for `topic` most similar to `query`, most similar first.

    Each result is {"chunk_text", "page_number", "filename", "score"}.
    """
    query_embedding = embed_text(query)

    conn = db.get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.chunk_text, c.page_number, c.embedding, d.filename
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE d.topic = %s;
            """,
            (topic,),
        )
        rows = cur.fetchall()

    scored = []
    for chunk_text, page_number, embedding, filename in rows:
        score = cosine_similarity(query_embedding, embedding)
        scored.append(
            {
                "chunk_text": chunk_text,
                "page_number": page_number,
                "filename": filename,
                "score": score,
            }
        )

    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    # python -m rag.retrieve dwdm_osnr "what is OSNR?"
    if len(sys.argv) != 3:
        print('Usage: python -m rag.retrieve <topic> "<question>"')
        sys.exit(1)

    topic_arg, query_arg = sys.argv[1], sys.argv[2]
    results = search_topic(topic_arg, query_arg, top_k=3)

    for r in results:
        print(f"[{r['filename']} p.{r['page_number']}] score={r['score']:.3f}")
        print(r["chunk_text"][:200])
        print()
