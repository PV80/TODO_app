"""Tests for the todo CLI helpers."""
from pathlib import Path
import sys
import json

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import todo


def test_add_and_list_tasks(tmp_path: Path) -> None:
    data_file = tmp_path / "todos.json"

    first = todo.add_task("Write tests", data_file)
    second = todo.add_task("Run pytest", data_file)

    assert first["id"] == 1
    assert second["id"] == 2

    tasks = todo.list_tasks(data_file)
    assert len(tasks) == 2
    assert tasks[0]["text"] == "Write tests"
    assert tasks[1]["text"] == "Run pytest"

    stored = json.loads(data_file.read_text(encoding="utf-8"))
    assert stored == tasks


def test_complete_task_marks_done(tmp_path: Path) -> None:
    data_file = tmp_path / "todos.json"
    task = todo.add_task("Finish feature", data_file)

    updated = todo.complete_task(task["id"], data_file)
    assert updated["done"] is True

    tasks = todo.list_tasks(data_file)
    assert tasks[0]["done"] is True


def test_remove_task_deletes_entry(tmp_path: Path) -> None:
    data_file = tmp_path / "todos.json"
    task = todo.add_task("Clean up", data_file)

    removed = todo.remove_task(task["id"], data_file)
    assert removed == task

    assert todo.list_tasks(data_file) == []


def test_cli_integration(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    data_file = tmp_path / "todos.json"

    todo.main(["--file", str(data_file), "add", "Read book"])
    todo.main(["--file", str(data_file), "complete", "1"])
    todo.main(["--file", str(data_file), "list"])

    captured = capsys.readouterr()
    # The last CLI call prints the list output.
    assert "[x] 1: Read book" in captured.out

    todo.main(["--file", str(data_file), "remove", "1"])
    todo.main(["--file", str(data_file), "list"])
    captured = capsys.readouterr()
    assert "No tasks found." in captured.out
