# Hello, Claude Code

## What this is
A minimal "hello world" project that calls the Claude API from Python. It sends
one message to Claude and prints the reply — the smallest possible example of
a Python script talking to Claude programmatically (as opposed to using the
claude.ai chat interface).

## Setup
1. Create a virtual environment (an isolated copy of Python just for this
   project, so its packages don't affect anything else on your machine):
   ```
   python -m venv .venv
   ```
2. Activate it (Windows PowerShell):
   ```
   .venv\Scripts\Activate.ps1
   ```
   Your terminal prompt should now start with `(.venv)`. You'll need to run
   this activate command again every time you open a new terminal to work on
   this project.
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Get an API key from console.anthropic.com (Settings → API Keys), then copy
   `.env.example` to a new file named `.env` and paste your real key in:
   ```
   ANTHROPIC_API_KEY=your-real-key-here
   ```
   `.env` is listed in `.gitignore` and will never be committed to git — only
   `.env.example` (with a fake placeholder) is tracked.

## How to run
With the virtual environment activated:
```
python src/main.py
```
This should print a short reply from Claude in the terminal.

note :- incase you are in wrong venv :- deactivate
cd "C:\Users\VARUN TYAGI\Desktop\Claudecodeprojects\Claude dev journey\01-hello-claude-code"
.\.venv\Scripts\Activate.ps1
python src/main.py

