"""Orchestrator for Project 12's RAG backend.

Unlike Project 10's orchestrator, this one does no classification --
the user picks the topic themselves from the frontend's dropdown, so
by the time a question reaches here we already know which of the four
topics it belongs to. This orchestrator's job is pure routing: given a
topic and a query, call the subagent responsible for that topic.

Kept as its own file (rather than inlining the dict into main.py later)
so the FastAPI layer just calls route() and doesn't need to know
anything about how topics map to subagents.
"""

from subagents import dwdm_osnr, ethernet, ip, others

_SUBAGENTS = {
    "dwdm_osnr": dwdm_osnr.answer,
    "ethernet": ethernet.answer,
    "ip": ip.answer,
    "others": others.answer,
}


def route(topic: str, query: str) -> dict:
    """Dispatch `query` to the subagent responsible for `topic`.

    Raises ValueError if `topic` isn't one of the four recognized topics.
    """
    try:
        subagent_answer = _SUBAGENTS[topic]
    except KeyError:
        raise ValueError(
            f"Unknown topic '{topic}'. Expected one of: {', '.join(_SUBAGENTS)}"
        )
    return subagent_answer(query)
