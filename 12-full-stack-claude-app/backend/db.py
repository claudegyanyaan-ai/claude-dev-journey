"""
Database connection and schema setup for the full-stack Claude app backend.

This module owns two things:
1. get_conn(), which returns a live psycopg2 connection to the Postgres
   database named by DATABASE_URL (loaded from .env) -- reconnecting
   automatically if the held connection has gone stale.
2. create_tables(), which creates the app's tables if they don't
   already exist.

Why get_conn() instead of one connection opened at import time: Neon is
serverless Postgres and closes idle connections (and can suspend the
underlying compute) after a period of inactivity. A single connection
object opened once when the FastAPI process starts does NOT survive a
gap of a few quiet minutes -- the next query fails with something like
"SSL connection has been closed unexpectedly". Every caller in this
project goes through get_conn() rather than holding a module-level
`conn` directly, so a dropped connection gets silently replaced instead
of crashing the next request.

Run this file directly (`python db.py`) to set up the schema as a one-off
step before starting the API.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

_conn = None


def get_conn():
    """Return a live connection, reconnecting if the held one is closed
    or has gone stale (e.g. Neon closed it after being idle).
    """
    global _conn

    if _conn is not None and not _conn.closed:
        try:
            with _conn.cursor() as cur:
                cur.execute("SELECT 1;")
            return _conn
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            pass  # fall through and reconnect below

    _conn = psycopg2.connect(DATABASE_URL)
    return _conn


def create_tables():
    """Create the app's tables if they don't exist."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                topic TEXT NOT NULL CHECK (
                    topic IN ('dwdm_osnr', 'ethernet', 'ip', 'others')
                ),
                filename TEXT NOT NULL,
                uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                document_id INTEGER NOT NULL REFERENCES documents(id),
                page_number INTEGER,
                chunk_text TEXT NOT NULL,
                embedding JSON
            );
        """)

        # Project 13: one row per /ask call, logging its REAL token spend
        # (read off Claude's response.usage, not estimated). Doubles as the
        # rate-limit counter's source of truth -- see rate_limit.py.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usage_log (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL REFERENCES users(username),
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                input_tokens INTEGER NOT NULL,
                output_tokens INTEGER NOT NULL,
                api_calls INTEGER NOT NULL,
                estimated_cost_usd NUMERIC(10, 6) NOT NULL
            );
        """)

    conn.commit()


def create_user(username: str, password_hash: str) -> None:
    """Insert a new user row. Caller is responsible for hashing the password first."""
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s);",
                (username, password_hash),
            )


def get_user_by_username(username: str) -> str | None:
    """Return the stored password_hash for `username`, or None if no such user exists."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT password_hash FROM users WHERE username = %s;",
            (username,),
        )
        row = cur.fetchone()
    return row[0] if row else None


if __name__ == "__main__":
    create_tables()
    print("Tables created (or already existed): users, documents, chunks, usage_log.")
