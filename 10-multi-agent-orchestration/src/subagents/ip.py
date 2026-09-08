"""IP/networking-fundamentals domain subagent: answers questions using docs/ip/ only."""

import os
import sys

from dotenv import load_dotenv

from src.rag_core import answer_from_index

INDEX_DIR = "data/index/ip"

SYSTEM_PROMPT = """\
You are a technical assistant specializing in IP networking fundamentals \
(the OSI model, the network layer, routers, gateways, firewalls, and \
LAN/MAN/WAN concepts). Answer using ONLY the excerpts provided below. \
Do not use outside knowledge, even if you happen to know the answer.

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

    q = " ".join(sys.argv[1:]) or "What does a router do?"
    result = answer(q)
    print(f"[pages referenced: {result['pages_referenced']}]\n")
    print(result["answer"])
