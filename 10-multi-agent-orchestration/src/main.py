"""CLI entry point: an interactive loop, one question at a time, until you quit.

Each question is a fresh, independent call through orchestrator.route() --
this loop is the only thing that persists across questions in this
session; no conversation history is shared between questions or between
subagents, which is the point (see orchestrator.py's docstring).
"""

import os
import sys

from dotenv import load_dotenv

from src.orchestrator import route, _print_trace


def main() -> None:
    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY isn't set. Copy .env.example to .env and add your key.")
        sys.exit(1)

    print("Multi-agent networking Q&A -- ask about DWDM/OSNR, Ethernet, or IP fundamentals.")
    print("Type 'quit' to exit.\n")

    while True:
        try:
            query = input("> ").strip()
        except EOFError:
            break
        if not query or query.lower() in {"quit", "exit"}:
            break

        _print_trace(route(query))
        print()


if __name__ == "__main__":
    main()
