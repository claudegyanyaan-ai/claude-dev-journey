"""CLI entry point: question in, grounded+cited answer out. The fast, repeated step.

Retrieves the top-k chunks for the question (retrieve.py), then sends them
to Claude as the *only* allowed source of truth -- the system prompt below
is where grounding and citation are actually enforced, not a similarity
threshold. Even an unrelated question still retrieves *some* chunks (cosine
similarity always returns a ranking); it's Claude's own judgment, guided by
the system prompt, that has to recognize when those excerpts don't actually
answer the question and say so instead of falling back to general knowledge.
"""

import os
import sys

import anthropic
from dotenv import load_dotenv

from retrieve import retrieve

MODEL_NAME = "claude-haiku-4-5"
TOP_K = 4

SYSTEM_PROMPT = """\
You are a technical assistant that answers questions using ONLY the \
excerpts provided below, drawn from a document on optical amplifiers and \
optical networking.

Rules:
- Answer using only the information in the excerpts. Do not use outside \
knowledge, even if you happen to know the answer.
- If the excerpts don't contain enough information to answer the \
question, say so plainly instead of guessing or answering from general \
knowledge.
- After your answer, add a line starting with "Source:" listing the \
section number(s) and heading(s) you actually drew from, e.g. \
"Source: Section 1.3.2 - Noise Figure". If you could not answer from the \
excerpts, omit this line.\
"""


def ask(query: str, k: int = TOP_K) -> str:
    """Retrieve the top-k chunks for `query` and return Claude's grounded,
    cited answer as plain text."""
    chunks = retrieve(query, k=k)

    excerpts = "\n\n".join(
        f"[Section {c['section']} - {c['heading']}, "
        f"pages {c['pages'][0]}-{c['pages'][1]}]\n{c['text']}"
        for c in chunks
    )
    user_message = f"Excerpts:\n\n{excerpts}\n\nQuestion: {query}"

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    return "\n".join(block.text for block in response.content if block.type == "text")


if __name__ == "__main__":
    load_dotenv()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY isn't set. Copy .env.example to .env and add "
            "your key before running ask.py."
        )
        sys.exit(1)

    if len(sys.argv) < 2:
        print('Usage: python src/ask.py "your question here"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    try:
        answer = ask(query)
    except FileNotFoundError:
        print(
            "No index found under data/index/. Run `python src/build_index.py` "
            "first to build it from docs/osnr.pdf."
        )
        sys.exit(1)

    print(answer)
