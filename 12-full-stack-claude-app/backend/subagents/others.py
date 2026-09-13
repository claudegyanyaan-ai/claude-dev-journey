"""Subagent for the "Others" topic -- user-uploaded documents that don't
fit DWDM/OSNR, Ethernet, or IP.

Thin on purpose, like the other three subagents: it delegates to
rag.answer's shared answer_question(). Kept separate specifically
because this is the category requirement #5 called out -- documents
here are unpredictable in subject matter, so this is the isolated place
to add "others"-specific handling later (e.g. a looser or more
cautious prompt) without touching the other three topics.
"""

from rag.answer import answer_question

TOPIC = "others"


def answer(query: str) -> dict:
    """Answer a question scoped to the Others topic."""
    return answer_question(TOPIC, query)
