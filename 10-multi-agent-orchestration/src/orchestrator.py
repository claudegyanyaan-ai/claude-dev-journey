"""Routes a user query to the correct domain subagent.

Classification is done by asking Claude itself which of the three domains
a query belongs to, rather than keyword matching -- this is the actual
orchestrator/subagent pattern Project 10 is about: one agent (Claude,
prompted only to classify) decides where to send the work, then a
specialist subagent answers it using its own isolated context -- each
subagent's Claude call only ever sees its own retrieved excerpts, never
the classifier's prompt or any other subagent's conversation.

route()'s return value is a full trace of the pipeline, not just the
final answer: which subagent got picked, which document that subagent is
scoped to, and which exact pages of that document were retrieved and sent
as context. Nothing here is Claude's self-report -- it's read directly
from the classifier's own output and from retrieve()'s chunk metadata, so
it says what the code actually did.
"""

import os
import sys

import anthropic
from dotenv import load_dotenv

from src.subagents import dwdm_osnr, ethernet, ip

CLASSIFY_MODEL = "claude-haiku-4-5"

SUBAGENTS = {
    "dwdm_osnr": dwdm_osnr.answer,
    "ethernet": ethernet.answer,
    "ip": ip.answer,
}

SOURCE_PDFS = {
    "dwdm_osnr": "docs/dwdm_osnr/dwdm_osnr.pdf",
    "ethernet": "docs/ethernet/ethernet.pdf",
    "ip": "docs/ip/IP.pdf",
}

CLASSIFY_SYSTEM_PROMPT = """\
You are a query router for a networking help system with three specialist \
subagents:
- dwdm_osnr: DWDM, OSNR, optical amplifiers, EDFAs, noise figure, optical \
networking
- ethernet: Ethernet standards, cabling, MAC addressing, hubs/switches, LAN
- ip: IP networking fundamentals, OSI model, routers, gateways, firewalls

Given a user's question, respond with ONLY one word: the domain name it \
belongs to (dwdm_osnr, ethernet, or ip). No explanation, no punctuation.\
"""


def classify_domain(query: str) -> str:
    """Ask Claude which of the three domains the query belongs to."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=CLASSIFY_MODEL,
        max_tokens=10,
        system=CLASSIFY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": query}],
    )
    text = "".join(b.text for b in response.content if b.type == "text").strip().lower()
    if text not in SUBAGENTS:
        raise ValueError(
            f"Classifier returned {text!r}, expected one of {list(SUBAGENTS)}"
        )
    return text


def route(query: str) -> dict:
    """Classify the query, dispatch it to the matching subagent, return the
    full trace: which domain, which source document, which pages, and the
    answer itself."""
    domain = classify_domain(query)
    result = SUBAGENTS[domain](query)
    return {
        "domain": domain,
        "source_pdf": SOURCE_PDFS[domain],
        "pages_referenced": result["pages_referenced"],
        "answer": result["answer"],
    }


def _print_trace(result: dict) -> None:
    print(f"[orchestrator routed to subagent: {result['domain']}]")
    print(f"[document: {result['source_pdf']}]")
    print(f"[pages referenced: {result['pages_referenced']}]\n")
    print(result["answer"])


if __name__ == "__main__":
    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY isn't set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print('Usage: python -m src.orchestrator "your question here"')
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    _print_trace(route(query))
