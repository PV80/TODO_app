"""Simple command-line TODO application.

This module implements a small TODO manager that stores tasks in a JSON
file.  It can be used as a CLI (``python todo.py <command>``) and provides a
few helper functions that can be reused in other contexts or tests.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, List, Dict, Any

# Default path for storing TODO entries.  This file lives next to the script
# and contains a JSON array of task dictionaries: {"id": int, "text": str,
# "done": bool}.
DATA_FILE = Path(__file__).with_name("todos.json")

Task = Dict[str, Any]


def load_tasks(data_file: Path = DATA_FILE) -> List[Task]:
    """Load task dictionaries from *data_file*.

    If the file does not exist yet the function returns an empty list.
    """
    if not data_file.exists():
        return []
    with data_file.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_tasks(tasks: Iterable[Task], data_file: Path = DATA_FILE) -> None:
    """Persist *tasks* into *data_file* as JSON.

    The file is created along with parent directories when necessary.
    """
    data_file.parent.mkdir(parents=True, exist_ok=True)
    with data_file.open("w", encoding="utf-8") as fh:
        json.dump(list(tasks), fh, indent=2)


def _generate_id(tasks: Iterable[Task]) -> int:
    """Return a monotonically increasing identifier for a new task."""
    max_id = 0
    for task in tasks:
        try:
            max_id = max(max_id, int(task["id"]))
        except (KeyError, TypeError, ValueError):
            # Ignore malformed entries; the caller can decide how to handle
            # them later.  We simply skip them when calculating the new id.
            continue
    return max_id + 1


def add_task(text: str, data_file: Path = DATA_FILE) -> Task:
    """Add a new task with *text* to the task list stored at *data_file*."""
    tasks = load_tasks(data_file)
    task: Task = {"id": _generate_id(tasks), "text": text, "done": False}
    tasks.append(task)
    save_tasks(tasks, data_file)
    return task


def list_tasks(data_file: Path = DATA_FILE) -> List[Task]:
    """Return the list of tasks stored at *data_file*."""
    return load_tasks(data_file)


def complete_task(task_id: int, data_file: Path = DATA_FILE) -> Task:
    """Mark the task identified by *task_id* as completed."""
    tasks = load_tasks(data_file)
    for task in tasks:
        if task.get("id") == task_id:
            task["done"] = True
            save_tasks(tasks, data_file)
            return task
    raise ValueError(f"Task with id {task_id} was not found.")


def remove_task(task_id: int, data_file: Path = DATA_FILE) -> Task:
    """Remove the task identified by *task_id* from the list."""
    tasks = load_tasks(data_file)
    for index, task in enumerate(tasks):
        if task.get("id") == task_id:
            removed = tasks.pop(index)
            save_tasks(tasks, data_file)
            return removed
    raise ValueError(f"Task with id {task_id} was not found.")


def _build_parser() -> argparse.ArgumentParser:
    """Create and configure the top-level argument parser."""
    parser = argparse.ArgumentParser(description="Simple TODO list manager")
    parser.add_argument(
        "--file",
        type=Path,
        default=DATA_FILE,
        help="Path to the todos.json file (defaults to todos.json next to the script).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("text", help="Text describing the task")

    subparsers.add_parser("list", help="List all tasks")

    complete_parser = subparsers.add_parser("complete", help="Mark a task as done")
    complete_parser.add_argument("id", type=int, help="ID of the task to complete")

    remove_parser = subparsers.add_parser("remove", help="Delete a task")
    remove_parser.add_argument("id", type=int, help="ID of the task to remove")

    return parser


def _format_task(task: Task) -> str:
    """Return a human-readable representation of a task."""
    status = "x" if task.get("done") else " "
    return f"[{status}] {task.get('id')}: {task.get('text')}"


def main(argv: List[str] | None = None) -> int:
    """Entry point for the command line interface."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    data_file: Path = args.file

    try:
        if args.command == "add":
            task = add_task(args.text, data_file)
            print(f"Added task {task['id']}: {task['text']}")
        elif args.command == "list":
            tasks = list_tasks(data_file)
            if not tasks:
                print("No tasks found.")
            else:
                for task in tasks:
                    print(_format_task(task))
        elif args.command == "complete":
            task = complete_task(args.id, data_file)
            print(f"Completed task {task['id']}.")
        elif args.command == "remove":
            task = remove_task(args.id, data_file)
            print(f"Removed task {task['id']}.")
        else:
            parser.error("Unknown command")
    except ValueError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
