---
description: Run a networking question through this project's orchestrator
  (routes to the DWDM/OSNR, Ethernet, or IP subagent, prints the routing
  trace, then the grounded answer).
argument-hint: [your networking question]
allowed-tools: Bash
disable-model-invocation: true
---

Run the question in `$ARGUMENTS` through this project's multi-agent
orchestrator and show the result as-is.

## Steps

1. Confirm you're working from the `10-multi-agent-orchestration` project
   folder — the orchestrator, venv, and indexes all live here, not at the
   repo root.
2. Confirm `ANTHROPIC_API_KEY` is set (a real `.env` exists, copied from
   `.env.example`) and all three indexes exist under
   `data/index/{dwdm_osnr,ethernet,ip}/` (each needs `chunks.json`,
   `embeddings.npy`, `meta.json`). If either is missing, say so plainly
   and stop rather than guessing or trying to rebuild anything.
3. Run, from that project folder, using its venv's Python:
   ```
   python -m src.orchestrator "$ARGUMENTS"
   ```
4. Show the full output exactly as printed — the three trace lines
   (`[orchestrator routed to subagent: ...]`, `[document: ...]`,
   `[pages referenced: ...]`) followed by the answer. Don't summarize,
   reformat, or drop the trace lines.
