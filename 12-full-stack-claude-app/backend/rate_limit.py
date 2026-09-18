"""Per-user daily request cap for Project 13's cost/rate-limit work.

Keeps the app's API spend bounded: no matter what a user does, they can
trigger at most DAILY_LIMIT calls into the RAG pipeline -- and therefore
at most DAILY_LIMIT worth of Claude API calls -- per calendar day (UTC).

Counts against `usage_log` rather than a separate counter table: one row
is written there per successful /ask call (see usage.py), so "how many
requests today" and "how much did they cost" both read from the same
source of truth instead of two counters that could silently drift apart.
"""

from fastapi import HTTPException

import db

DAILY_LIMIT = 10


def get_usage_today(username: str) -> int:
    """Count `username`'s /ask requests since midnight UTC today."""
    conn = db.get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*) FROM usage_log
            WHERE username = %s AND created_at >= date_trunc('day', NOW());
            """,
            (username,),
        )
        return cur.fetchone()[0]


def check_rate_limit(username: str) -> int:
    """Raise 429 if `username` has already used today's DAILY_LIMIT.

    Returns how many requests they have left today (before this one),
    so main.py can hand that back to the frontend.
    """
    used = get_usage_today(username)
    remaining = DAILY_LIMIT - used
    if remaining <= 0:
        raise HTTPException(
            status_code=429,
            detail=(
                f"Daily limit of {DAILY_LIMIT} questions reached. "
                "Resets at midnight UTC."
            ),
        )
    return remaining
