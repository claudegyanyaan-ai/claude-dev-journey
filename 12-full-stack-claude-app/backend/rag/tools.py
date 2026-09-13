"""The search_docs tool -- defined and implemented exactly once here, then
used two different ways elsewhere in the project:

1. rag.answer wires this into a live Anthropic tool-use loop, so Claude
   itself decides to call it before answering (with `topic` pinned by
   whichever subagent is asking -- Claude only ever supplies `query`).
2. mcp_server.py wraps execute_search_docs() as a real MCP tool, so an
   external MCP client (Claude Desktop, Claude Code) can call it too,
   with full control over both `topic` and `query`.

Keeping the actual retrieval logic in one function means both integration
paths stay in sync automatically -- there's nothing to keep duplicated in
step with each other.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from rag.retrieve import search_topic

VALID_TOPICS = ("dwdm_osnr", "ethernet", "ip", "others")


def execute_search_docs(topic: str, query: str, top_k: int = 3) -> str:
    """Run the actual retrieval and format results as a single text block
    suitable for a tool_result, citing filename + page for every excerpt.
    """
    if topic not in VALID_TOPICS:
        return f"Invalid topic '{topic}'. Must be one of: {', '.join(VALID_TOPICS)}."

    chunks = search_topic(topic, query, top_k=top_k)
    if not chunks:
        return "No matching excerpts found."

    return "\n\n".join(
        f"[Source: {c['filename']}, page {c['page_number']}]\n{c['chunk_text']}"
        for c in chunks
    )


def search_docs_tool_schema(topic: str) -> dict:
    """Anthropic tool-use schema for search_docs, scoped to a single fixed
    topic. Claude only ever gets to supply `query` -- `topic` is baked into
    the description and closed over by the caller, so the model has no way
    to search outside the topic the user selected in the UI.
    """
    return {
        "name": "search_docs",
        "description": (
            f"Search the {topic} documents for excerpts relevant to a query. "
            "Returns the most relevant excerpts, each tagged with its source "
            "filename and page number. You must call this before answering."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query -- typically the user's question.",
                }
            },
            "required": ["query"],
        },
    }
