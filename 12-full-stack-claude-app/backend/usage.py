"""Token-usage and cost tracking for Project 13.

Every /ask call logs exactly how many tokens it actually spent, read off
Claude's own `response.usage` field -- not estimated after the fact from
question length. Same "measure the real thing, don't trust a guess"
instinct as this ladder's Project 11 eval work.

Pricing is Claude Haiku 4.5's published per-million-token rate as of
2026-09 ($1/MTok input, $5/MTok output, confirmed via web search since
this is exactly the kind of present-day fact that can go stale) --
update PRICE_PER_MTOK below if Anthropic changes it; nothing else in
this file depends on the exact numbers being current.
"""

import db

INPUT_PRICE_PER_MTOK = 1.00
OUTPUT_PRICE_PER_MTOK = 5.00


def estimate_cost_usd(input_tokens: int, output_tokens: int) -> float:
    return (
        (input_tokens / 1_000_000) * INPUT_PRICE_PER_MTOK
        + (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_MTOK
    )


def log_usage(username: str, input_tokens: int, output_tokens: int, api_calls: int) -> float:
    """Record one /ask call's real token spend.

    Returns the estimated cost (USD) so the caller can report it back
    without recomputing.
    """
    cost = estimate_cost_usd(input_tokens, output_tokens)
    conn = db.get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO usage_log
                    (username, input_tokens, output_tokens, api_calls, estimated_cost_usd)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (username, input_tokens, output_tokens, api_calls, cost),
            )
    return cost
