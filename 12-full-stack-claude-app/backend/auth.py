"""Password hashing and JWT issuing/verification for Project 12.

Same pattern as web-app-dev-mentor's Project 5: bcrypt for passwords
(never store or compare plain text), a signed JWT for sessions (so
main.py's routes can trust "this request is really user X" without
hitting the database on every single call -- just verify the signature).
"""

import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """One-way hash a plain-text password for storage."""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Check a plain-text password against a stored hash."""
    return pwd_context.verify(password, password_hash)


def create_access_token(username: str) -> str:
    """Issue a signed JWT for `username`, valid for JWT_EXPIRY_HOURS."""
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> str | None:
    """Decode and validate a JWT. Returns the username, or None if the
    token is invalid, tampered with, or expired.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
