"""Loads the index, embeds a query, returns top-k chunks. The fast, repeated step.

Retrieval is a plain in-memory cosine similarity search over data/index/'s
embeddings -- no vector database. At this document's scale (under 100
chunks), a NumPy dot product over all of them is simpler than standing up
Chroma/FAISS and just as fast; see the project spec's storage/retrieval
design choice for the full reasoning.
"""

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

_model = None  # loaded lazily, once per process -- avoid reloading per query


def _load_model(model_name: str) -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(model_name)
    return _model


def _normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=-1, keepdims=True)
    norms[norms == 0] = 1  # avoid divide-by-zero for a theoretical zero vector
    return vectors / norms


def load_index(index_dir: str = "data/index") -> dict:
    """Load the chunks, embeddings, and metadata written by build_index.py."""
    index_path = Path(index_dir)
    with open(index_path / "chunks.json", encoding="utf-8") as f:
        chunks = json.load(f)
    embeddings = np.load(index_path / "embeddings.npy")
    with open(index_path / "meta.json", encoding="utf-8") as f:
        meta = json.load(f)

    if len(chunks) != embeddings.shape[0]:
        raise ValueError(
            f"Index is inconsistent: {len(chunks)} chunks but "
            f"{embeddings.shape[0]} embeddings. Try rebuilding with build_index.py."
        )

    # Normalize defensively rather than assume the saved embeddings are
    # already unit-length -- cheap at this scale either way.
    return {"chunks": chunks, "embeddings": _normalize(embeddings), "meta": meta}


def retrieve(query: str, k: int = 4, index_dir: str = "data/index") -> list[dict]:
    """Return the top-k chunks most similar to `query`, most similar first.

    Each returned dict is the chunk's original fields (section, chapter,
    heading, text, pages) plus a "score" -- the cosine similarity, in
    [-1, 1], between the chunk and the query.
    """
    index = load_index(index_dir)
    model = _load_model(index["meta"]["model"])

    query_vec = model.encode([query])
    query_vec = _normalize(np.asarray(query_vec, dtype=np.float32))[0]

    scores = index["embeddings"] @ query_vec  # both sides unit-length -> dot == cosine
    top_k_idx = np.argsort(-scores)[:k]

    results = []
    for i in top_k_idx:
        chunk = dict(index["chunks"][i])
        chunk["score"] = float(scores[i])
        results.append(chunk)
    return results


if __name__ == "__main__":
    # Manual sanity check: run
    #   python src/retrieve.py "What is the quantum limit for noise figure?"
    # from the project root and eyeball whether the top hits look relevant.
    import sys

    query = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "What is the quantum limit for noise figure?"
    )
    print(f"Query: {query!r}\n")
    for r in retrieve(query):
        print(f"[{r['score']:.3f}] Section {r['section']} - {r['heading']} (pages {r['pages']})")
        print(f"  {r['text'][:150]!r}")
        print()
