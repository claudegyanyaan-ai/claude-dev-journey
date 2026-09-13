"""Answer a question about a topic, grounded in that topic's retrieved chunks.

Claude is given the search_docs tool and must call it before answering
(tool_choice forces this on the first turn). Unlike a fixed "search once,
then answer" sequence, this runs as a real loop: if Claude decides its
first search wasn't specific enough, it's allowed to call search_docs
again with a refined query before producing a final answer. A round cap
(MAX_TOOL_ROUNDS) stops this from running away if Claude never settles
on an answer.

The strict-grounding guarantee doesn't rely on Claude behaving -- `topic`
is pinned by whichever subagent calls answer_question() and is never
something Claude's tool call can override; Claude only ever supplies the
search query. The same search_docs logic also backs mcp_server.py, so an
external MCP client uses the exact same retrieval code.
"""

import sys
from pathlib import Path

# db.py lives one directory up (backend/); this file lives in backend/rag/.
sys.path.append(str(Path(__file__).resolve().parent.parent))

import anthropic

from rag.retrieve import search_topic
from rag.tools import search_docs_tool_schema

ANSWER_MODEL = "claude-haiku-4-5"
MAX_TOOL_ROUNDS = 3

SYSTEM_PROMPT = """You answer questions using ONLY excerpts you retrieve with the search_docs tool.

Rules:
- You MUST call search_docs before answering. Never answer from memory or general knowledge.
- If the first search's results aren't specific enough to answer well, you may call search_docs again with a refined query. Do this silently -- don't narrate that you're searching again, just call the tool.
- Base your answer entirely on what search_docs returns. Do not use any outside knowledge, even if you are confident it is correct.
- If the returned excerpts do not contain enough information to answer the question, respond exactly: "The provided documents don't contain information about this."
- Do not guess, infer beyond what the excerpts state, or fill gaps with general knowledge.
- Keep the answer concise and directly tied to what the excerpts say."""


def _dedupe_sources(sources: list[dict]) -> list[dict]:
    seen = set()
    deduped = []
    for s in sources:
        key = (s["filename"], s["page_number"])
        if key not in seen:
            seen.add(key)
            deduped.append(s)
    return deduped


def answer_question(topic: str, query: str) -> dict:
    """Ask Claude to answer `query`, requiring it to call search_docs
    (scoped to `topic`) at least once, and allowing up to MAX_TOOL_ROUNDS
    total search calls if it needs to refine its query.

    Returns {"answer": <text>, "sources": [{"filename", "page_number"}, ...]}.
    Sources list every chunk returned across all search rounds Claude
    actually made -- an honest record of what context was used, not a
    self-report from the model.
    """
    client = anthropic.Anthropic()
    tool_schema = search_docs_tool_schema(topic)
    messages = [{"role": "user", "content": query}]
    sources = []

    # Force the tool on round 1 -- grounding isn't optional. After that,
    # let Claude decide whether it needs to search again or can answer.
    tool_choice = {"type": "tool", "name": "search_docs"}
    response = None

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.messages.create(
            model=ANSWER_MODEL,
            max_tokens=400,
            system=SYSTEM_PROMPT,
            tools=[tool_schema],
            tool_choice=tool_choice,
            messages=messages,
        )

        tool_use_block = next(
            (b for b in response.content if b.type == "tool_use"), None
        )

        if tool_use_block is None:
            # No further tool call -- this is Claude's final answer.
            answer_text = "\n".join(
                b.text for b in response.content if b.type == "text"
            )
            return {"answer": answer_text, "sources": _dedupe_sources(sources)}

        search_query = tool_use_block.input.get("query", query)
        chunks = search_topic(topic, search_query, top_k=3)
        sources.extend(
            {"filename": c["filename"], "page_number": c["page_number"]}
            for c in chunks
        )
        tool_result_text = (
            "\n\n".join(
                f"[Source: {c['filename']}, page {c['page_number']}]\n{c['chunk_text']}"
                for c in chunks
            )
            or "No matching excerpts found."
        )

        messages.append({"role": "assistant", "content": response.content})
        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_block.id,
                        "content": tool_result_text,
                    }
                ],
            }
        )

        # Only round 1 is forced -- after that, let Claude choose.
        tool_choice = {"type": "auto"}

    # Exhausted MAX_TOOL_ROUNDS worth of searches. Force a real final
    # answer by making one more call WITHOUT the `tools` parameter at all
    # -- Claude has no way to request another search, so it must produce
    # text using only what's already been retrieved. This is what
    # actually guarantees an answer instead of leftover "let me search
    # again" narration from a model that didn't stop calling the tool.
    final_response = client.messages.create(
        model=ANSWER_MODEL,
        max_tokens=400,
        system=(
            SYSTEM_PROMPT
            + "\n\nYou have used all your available searches. Answer now "
            "using only the excerpts already retrieved above -- do not "
            "request another search."
        ),
        messages=messages,
    )
    answer_text = "\n".join(
        b.text for b in final_response.content if b.type == "text"
    ).strip()
    if not answer_text:
        answer_text = "The provided documents don't contain information about this."
    return {"answer": answer_text, "sources": _dedupe_sources(sources)}


if __name__ == "__main__":
    # python -m rag.answer dwdm_osnr "what is OSNR?"
    if len(sys.argv) != 3:
        print('Usage: python -m rag.answer <topic> "<question>"')
        sys.exit(1)

    topic_arg, query_arg = sys.argv[1], sys.argv[2]
    result = answer_question(topic_arg, query_arg)

    print(result["answer"])
    print("\nSources:")
    for s in result["sources"]:
        print(f"- {s['filename']} p.{s['page_number']}")
