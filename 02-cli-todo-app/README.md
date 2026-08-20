# CLI To-Do App

## What this is
A command-line to-do list app written in Python. It supports adding tasks,
listing them, marking them done, and removing them — all stored in a simple
`tasks.json` file so your tasks persist between runs.

## Setup
No virtual environment or installation needed — this project only uses
Python's standard library. Just make sure you have Python installed.

## How to run

Add a task:
```
python src/main.py add "buy milk"
```

List all tasks (shows a checkbox next to each — `[ ]` for incomplete, `[x]` for done):
```
python src/main.py list
```

Mark a task done, using the number shown by `list`:
```
python src/main.py done 1
```

Remove a task, using the number shown by `list`:
```
python src/main.py remove 1
```

If you give `done` or `remove` a number that doesn't exist, it prints an
error instead of crashing, e.g. `No task number 99.`

## How to run the test
```
python tests/test_main.py
```
This runs against a throwaway test file, not your real `tasks.json`, so it's
always safe to run.
