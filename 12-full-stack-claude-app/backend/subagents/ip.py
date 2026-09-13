"""Subagent for the IP topic.

Thin on purpose: for now it just delegates to rag.answer's shared
answer_question(). Kept as its own file so IP-specific handling can be
added later without touching the other three topics.
"""

from rag.answer import answer_question

TOPIC = "ip"


def answer(query: str) -> dict:
    """Answer a question scoped to the IP topic."""
    return answer_question(TOPIC, query)
