"""DWDM/OSNR domain subagent: answers questions using docs/dwdm_osnr/ only."""

import os
import sys

from dotenv import load_dotenv

from src.rag_core import answer_from_index

INDEX_DIR = "data/index/dwdm_osnr"

SYSTEM_PROMPT = """\
You are a technical assistant specializing in DWDM and OSNR (optical \
amplifiers, noise figure, EDFAs, and optical networking). Answer using \
ONLY the excerpts provided below. Do not use outside knowledge, even if \
you happen to know the answer.

If the excerpts don't contain enough information to answer, say so \
plainly instead of guessing.\
"""


def answer(query: str) -> dict:
    return answer_from_index(query, INDEX_DIR, SYSTEM_PROMPT)


if __name__ == "__main__":
    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY isn't set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    q = " ".join(sys.argv[1:]) or "What is the quantum limit for noise figure?"
    result = answer(q)
    print(f"[pages referenced: {result['pages_referenced']}]\n")
    print(result["answer"])
