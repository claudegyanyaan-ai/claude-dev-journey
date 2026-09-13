"""Subagent for the DWDM/OSNR topic.

Thin on purpose: for now it just delegates to rag.answer's shared
answer_question(). The point of keeping it as its own file is to have a
place to add DWDM/OSNR-specific handling later (e.g. a tweaked prompt)
without touching the other three topics.
"""

from rag.answer import answer_question

TOPIC = "dwdm_osnr"


def answer(query: str) -> dict:
    """Answer a question scoped to the DWDM/OSNR topic."""
    return answer_question(TOPIC, query)
