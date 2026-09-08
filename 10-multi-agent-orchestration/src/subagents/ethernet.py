"""Ethernet domain subagent: answers questions using docs/ethernet/ only."""

import os
import sys

from dotenv import load_dotenv

from src.rag_core import answer_from_index

INDEX_DIR = "data/index/ethernet"

SYSTEM_PROMPT = """\
You are a technical assistant specializing in Ethernet networking \
(IEEE 802.3 standards, cabling types and distances, MAC addressing, \
hubs, switches, duplex modes, and LAN topology). Answer using ONLY the \
excerpts provided below. Do not use outside knowledge, even if you \
happen to know the answer.

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

    q = " ".join(sys.argv[1:]) or "What is the maximum cable length for 1000BASE-T?"
    result = answer(q)
    print(f"[pages referenced: {result['pages_referenced']}]\n")
    print(result["answer"])
