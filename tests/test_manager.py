from __future__ import annotations

from datetime import date, timedelta

import pytest

from task_manager import TaskManager


def test_add_and_list_tasks(tmp_path):
    storage = tmp_path / "tasks.json"
    manager = TaskManager(storage)

    first = manager.add_task("Task A", "First task", due_date=date.today())
    second = manager.add_task("Task B")

    assert first.id == 1
    assert second.id == 2

    tasks = manager.list_tasks()
    assert [task.title for task in tasks] == ["Task A", "Task B"]
    assert tasks[0].due_date == date.today()
    assert tasks[1].due_date is None

    reloaded = TaskManager(storage)
    titles = [task.title for task in reloaded.list_tasks()]
    assert titles == ["Task A", "Task B"]


def test_complete_task_updates_status(tmp_path):
    storage = tmp_path / "tasks.json"
    manager = TaskManager(storage)

    task = manager.add_task("Task A")
    assert not task.completed

    updated = manager.complete_task(task.id)
    assert updated.completed

    # Ensure persisted flag survives reload
    reloaded = TaskManager(storage)
    listed = reloaded.list_tasks()
    assert listed[0].completed is True

    with pytest.raises(KeyError):
        manager.complete_task(999)


def test_upcoming_tasks_filters_by_date(tmp_path):
    storage = tmp_path / "tasks.json"
    manager = TaskManager(storage)

    today = date.today()
    manager.add_task("Today", due_date=today)
    manager.add_task("Tomorrow", due_date=today + timedelta(days=1))
    manager.add_task("Later", due_date=today + timedelta(days=5))
    manager.add_task("No Due")
    done = manager.add_task("Done soon", due_date=today + timedelta(days=2))
    manager.complete_task(done.id)

    upcoming = manager.upcoming_tasks(within_days=3)
    assert [task.title for task in upcoming] == ["Today", "Tomorrow"]

    including_completed = manager.upcoming_tasks(within_days=3, include_completed=True)
    assert [task.title for task in including_completed] == [
        "Today",
        "Tomorrow",
        "Done soon",
    ]

    with pytest.raises(ValueError):
        manager.upcoming_tasks(within_days=-1)


def test_loading_from_empty_file_returns_no_tasks(tmp_path):
    storage = tmp_path / "tasks.json"
    storage.write_text("   \n", encoding="utf-8")

    manager = TaskManager(storage)
    assert manager.list_tasks() == []

    manager.add_task("Task A")
    assert [task.title for task in manager.list_tasks()] == ["Task A"]
