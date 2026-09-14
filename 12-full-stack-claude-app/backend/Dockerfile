# Base Python version matches the project's own local .venv (3.14), so
# there's no "works on my machine, breaks in the container" version drift.
FROM python:3.14-slim

# tesseract-ocr is a system-level program, not a Python package --
# pytesseract (in requirements.txt) is only a thin wrapper that shells out
# to this binary. Render's default "Python 3" runtime has no way to
# install an OS package like this, which is the whole reason this service
# needs a Dockerfile instead of Render's native buildpack.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copied and installed before the rest of the source so Docker can reuse
# this (slow) layer from cache on future builds, as long as
# requirements.txt itself hasn't changed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render injects $PORT at runtime and expects the process to bind to it --
# the shell form of CMD (not the ["exec", "form"] array form) is required
# here specifically so that $PORT actually gets expanded by the shell
# before uvicorn sees it.
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
