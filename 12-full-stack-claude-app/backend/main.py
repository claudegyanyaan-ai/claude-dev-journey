"""FastAPI app for Project 12: ties auth, the orchestrator, and the
upload pipeline into HTTP routes.

Routes:
- POST /signup  -- create a new user account
- POST /login   -- verify credentials, issue a JWT
- GET  /topics  -- list the 4 valid topics (for the frontend dropdown)
- POST /ask     -- ask a question about a topic (requires a valid token)
- POST /upload  -- upload a new PDF tagged with a topic (requires a valid token)

/signup and /login are the only routes reachable without a token. /ask
and /upload both depend on get_current_username(), which is the single
place a request's Authorization header actually gets checked -- the
auth boundary is enforced once here, not repeated per route.
"""

import os
import tempfile

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

import db
from auth import create_access_token, hash_password, verify_password, verify_token
from orchestrator import route
from rag.ingest import ingest_document
from rag.tools import VALID_TOPICS

app = FastAPI(title="Project 12 - Full-Stack Claude App")

# Tightened to the actual deployed frontend (Vercel) plus localhost for
# local development -- no longer wide open now that we've deployed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://docsassistant.vercel.app",
        "http://localhost:3000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()


class SignupRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AskRequest(BaseModel):
    topic: str
    query: str


def get_current_username(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Verify the request's Bearer token. Raises 401 if missing/invalid/expired."""
    username = verify_token(credentials.credentials)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return username


def _validate_topic(topic: str) -> None:
    if topic not in VALID_TOPICS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid topic '{topic}'. Must be one of: {', '.join(VALID_TOPICS)}",
        )


@app.post("/signup")
def signup(body: SignupRequest):
    if db.get_user_by_username(body.username) is not None:
        raise HTTPException(status_code=400, detail="Username already taken")
    db.create_user(body.username, hash_password(body.password))
    return {"message": "Account created"}


@app.post("/login")
def login(body: LoginRequest):
    password_hash = db.get_user_by_username(body.username)
    if password_hash is None or not verify_password(body.password, password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"access_token": create_access_token(body.username), "token_type": "bearer"}


@app.get("/topics")
def list_topics():
    return {"topics": list(VALID_TOPICS)}


@app.post("/ask")
def ask(body: AskRequest, username: str = Depends(get_current_username)):
    _validate_topic(body.topic)
    return route(body.topic, body.query)


@app.post("/upload")
def upload(
    topic: str = Form(...),
    file: UploadFile = File(...),
    username: str = Depends(get_current_username),
):
    _validate_topic(topic)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        chunk_count = ingest_document(tmp_path, topic, file.filename)
    finally:
        os.remove(tmp_path)

    return {
        "message": f"Uploaded and processed {file.filename}",
        "topic": topic,
        "chunks_inserted": chunk_count,
    }
