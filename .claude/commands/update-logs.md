---
description: Append a dated session log entry to the current project's
  chat-logs/ folder, following this repo's established prose-narrative log
  format.
argument-hint: [project-folder]
allowed-tools: Read, Write, Edit, Glob
disable-model-invocation: true
---

Append (or create) today's dated session log in the currently active
project's `chat-logs/` folder, in the narrative style already used across
this repo — see `06-your-first-mcp-server/chat-logs/2026-08-22_2054.md` as
the reference example.

## Steps

1. **Find the active project folder.**
   - If `$ARGUMENTS` names one (e.g. `07-claude-code-extensibility-lab`), use
     it directly.
   - Otherwise check root `PROGRESS.md` for a "Current project: Project N
     (...)" line as the primary signal, and cross-check against the
     numbered folders at repo root (`NN-kebab-case-name`; note the known
     exception `Project4_Single_Tool_Bot`, which doesn't follow the pattern).
   - If the signals disagree or nothing points clearly to one project, ask
     before proceeding — don't guess silently.

2. **Build today's log filename**: `YYYY-MM-DD_HHMM.md`, 24-hour time, no
   seconds or colons (matches existing filenames). Use the current date/time
   from context.

3. **Check for an existing log file for today** in
   `<project>/chat-logs/<today>*.md`.
   - If one exists, **append** new `##` sections to its end rather than
     overwriting — the reference example itself grew this way across a
     session (a later "Standing instruction (date)" section and a second
     "Status as of this update" section were appended after the fact).
   - If none exists, **create** the file with this header block first:
     ```
     # Session Log — Project N: <Project Title>
     Date: YYYY-MM-DD (Asia/Kolkata)

     ---
     ```
   - Create `chat-logs/` in the project folder first if it doesn't exist.

4. **Write the log as dense narrative prose, organized under `##` headers
   named after what actually happened this session** — not a fixed
   template, and not a raw transcript dump. Cover, as relevant: what was
   discussed or decided, what was built/debugged and why, any notable Q&A,
   and close with a "## Status as of this log" section. Match the reference
   example's tone: third person, past tense, bold for key decisions/terms,
   inline code for filenames/commands/functions, numbered or bulleted
   sub-lists for multi-part explanations.

5. Tell the user which file was created or updated and give a one-line
   summary of what got logged.
