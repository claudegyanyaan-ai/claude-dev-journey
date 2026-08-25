"""Orchestrates extract -> chunk -> embed -> save. The slow, one-time step.

Run this once (or whenever docs/osnr.pdf changes) to (re)build the index
under data/index/. retrieve.py / ask.py then load that index and never
touch the PDF or the embedding model themselves -- that's the fast,
repeated path, kept deliberately separate from this slow one.

Pipeline:
  1. extract.extract_pages()  -- OCR the PDF, per page (~70s for 40 pages)
  2. chunk.chunk_pages()      -- split into sections by heading
  3. drop near-empty chunks   -- parent headings with no intro text of
                                 their own (e.g. "2.4" immediately followed
                                 by "2.4.1") carry nothing worth embedding
  4. embed each chunk locally with sentence-transformers
  5. save chunks + embeddings to data/index/
"""

import json
import time
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

from chunk import chunk_pages
from extract import extract_pages

MODEL_NAME = "all-MiniLM-L6-v2"

# Chunks shorter than this are almost always a parent heading immediately
# followed by its first subsection, with no body text of its own (see
# chunk.py's docstring / Step 3 notes) -- nothing meaningful to embed.
MIN_CHUNK_CHARS = 20


def build_index(
    pdf_path: str = "docs/osnr.pdf",
    index_dir: str = "data/index",
) -> None:
    index_path = Path(index_dir)
    index_path.mkdir(parents=True, exist_ok=True)

    print(f"1/4  Extracting text from {pdf_path} (OCR -- this is the slow part)...")
    start = time.time()
    pages = extract_pages(pdf_path)
    print(f"     done in {time.time() - start:.0f}s ({len(pages)} pages)")

    print("2/4  Chunking by section heading...")
    all_chunks = chunk_pages(pages)
    chunks = [c for c in all_chunks if len(c["text"]) >= MIN_CHUNK_CHARS]
    dropped = len(all_chunks) - len(chunks)
    print(f"     {len(chunks)} chunks kept, {dropped} near-empty chunks dropped")

    print(f"3/4  Embedding {len(chunks)} chunks locally with {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    # Embed "Section <n> — <heading>" plus the body together, so a query
    # that names a topic close to the heading (e.g. "noise figure") matches
    # as well as one that only echoes the body wording.
    texts_to_embed = [
        f"Section {c['section']} — {c['heading']}\n{c['text']}" for c in chunks
    ]
    embeddings = model.encode(texts_to_embed, show_progress_bar=True)
    embeddings = np.asarray(embeddings, dtype=np.float32)

    print(f"4/4  Saving index to {index_path}/...")
    with open(index_path / "chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    np.save(index_path / "embeddings.npy", embeddings)
    with open(index_path / "meta.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "model": MODEL_NAME,
                "embedding_dim": int(embeddings.shape[1]),
                "chunk_count": len(chunks),
                "source_pdf": pdf_path,
            },
            f,
            indent=2,
        )

    print(
        f"\nDone. {len(chunks)} chunks, {embeddings.shape[1]}-dim embeddings "
        f"-> {index_path}/chunks.json, embeddings.npy, meta.json"
    )


if __name__ == "__main__":
    build_index()
