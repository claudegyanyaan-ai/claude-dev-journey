"""
Command-line to-do app.

Usage:
    python src/main.py add "task text"
"""
import argparse
import json
import os

# tasks.json lives in the project root (one level up from src/),
# regardless of what directory you run this script from.
TASKS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "tasks.json",
)


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(task_text):
    tasks = load_tasks()
    tasks.append({"task": task_text, "done": False})
    save_tasks(tasks)
    print(f'Added: "{task_text}"')


def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks yet.")
        return
    for i, task in enumerate(tasks, start=1):
        mark = "x" if task["done"] else " "
        print(f'{i}. [{mark}] {task["task"]}')


def mark_done(number):
    tasks = load_tasks()
    index = number - 1  # list numbering starts at 1; list indexing starts at 0
    if index < 0 or index >= len(tasks):
        print(f"No task number {number}.")
        return
    tasks[index]["done"] = True
    save_tasks(tasks)
    print(f'Marked done: "{tasks[index]["task"]}"')


def remove_task(number):
    tasks = load_tasks()
    index = number - 1
    if index < 0 or index >= len(tasks):
        print(f"No task number {number}.")
        return
    removed = tasks.pop(index)
    save_tasks(tasks)
    print(f'Removed: "{removed["task"]}"')


def main():
    parser = argparse.ArgumentParser(description="A simple command-line to-do app.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("task", help="The task text to add")

    subparsers.add_parser("list", help="List all tasks")

    done_parser = subparsers.add_parser("done", help="Mark a task as done")
    done_parser.add_argument("number", type=int, help="The task number to mark done")

    remove_parser = subparsers.add_parser("remove", help="Remove a task")
    remove_parser.add_argument("number", type=int, help="The task number to remove")

    args = parser.parse_args()

    if args.command == "add":
        add_task(args.task)
    elif args.command == "list":
        list_tasks()
    elif args.command == "done":
        mark_done(args.number)
    elif args.command == "remove":
        remove_task(args.number)


if __name__ == "__main__":
    main()
