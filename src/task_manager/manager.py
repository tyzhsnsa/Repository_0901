"""Core task manager logic and data structures."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, List, Optional


@dataclass(slots=True)
class Task:
    """Simple representation of a task tracked by the manager."""

    id: int
    title: str
    description: str = ""
    due_date: Optional[date] = None
    completed: bool = False

    def to_dict(self) -> dict:
        """Return a JSON-serialisable representation of the task."""

        data = asdict(self)
        if self.due_date is not None:
            data["due_date"] = self.due_date.isoformat()
        return data

    @classmethod
    def from_dict(cls, payload: dict) -> "Task":
        """Create a task instance from a dictionary."""

        raw_due = payload.get("due_date")
        due_date = None
        if raw_due:
            due_date = datetime.fromisoformat(raw_due).date()
        return cls(
            id=int(payload["id"]),
            title=str(payload["title"]),
            description=str(payload.get("description", "")),
            due_date=due_date,
            completed=bool(payload.get("completed", False)),
        )


class TaskManager:
    """Persist tasks on disk and expose helpers for managing them."""

    def __init__(self, storage_path: Path | str):
        self._storage_path = Path(storage_path)
        if self._storage_path.is_dir():
            raise IsADirectoryError(f"Storage path {self._storage_path} is a directory")
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def list_tasks(self, include_completed: bool = True) -> List[Task]:
        """Return all tasks, optionally filtering completed ones."""

        tasks = self._load_tasks()
        if include_completed:
            return tasks
        return [task for task in tasks if not task.completed]

    def add_task(
        self,
        title: str,
        description: str = "",
        *,
        due_date: date | datetime | str | None = None,
    ) -> Task:
        """Create a new task and persist it.

        The returned task includes an auto-incremented identifier.
        """

        tasks = self._load_tasks()
        next_id = 1 if not tasks else max(task.id for task in tasks) + 1
        task = Task(
            id=next_id,
            title=title,
            description=description,
            due_date=self._normalise_date(due_date),
        )
        tasks.append(task)
        self._write_tasks(tasks)
        return task

    def complete_task(self, task_id: int, *, completed: bool = True) -> Task:
        """Mark a task as complete or incomplete and persist the change."""

        tasks = self._load_tasks()
        for task in tasks:
            if task.id == task_id:
                task.completed = completed
                self._write_tasks(tasks)
                return task
        raise KeyError(f"Task with id {task_id} not found")

    def get_task(self, task_id: int) -> Task:
        """Return a task by identifier."""

        for task in self._load_tasks():
            if task.id == task_id:
                return task
        raise KeyError(f"Task with id {task_id} not found")

    def upcoming_tasks(
        self,
        *,
        within_days: int,
        include_completed: bool = False,
    ) -> List[Task]:
        """Return tasks whose due date is within *within_days* days.

        Tasks without a due date are excluded. Results are sorted by their
        due date ascending.
        """

        if within_days < 0:
            raise ValueError("within_days must be non-negative")

        today = date.today()
        limit = today + timedelta(days=within_days)

        results: List[Task] = []
        for task in self._load_tasks():
            if task.due_date is None:
                continue
            if not include_completed and task.completed:
                continue
            if today <= task.due_date <= limit:
                results.append(task)

        results.sort(key=lambda item: item.due_date)
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_tasks(self) -> List[Task]:
        if not self._storage_path.exists():
            return []

        contents = self._storage_path.read_text(encoding="utf-8")
        if not contents.strip():
            return []

        try:
            raw = json.loads(contents)
        except json.JSONDecodeError as exc:
            raise ValueError("Storage file is corrupted") from exc

        return [Task.from_dict(item) for item in raw]

    def _write_tasks(self, tasks: Iterable[Task]) -> None:
        serialisable = [task.to_dict() for task in tasks]
        self._storage_path.write_text(
            json.dumps(serialisable, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _normalise_date(value: date | datetime | str | None) -> Optional[date]:
        if value is None:
            return None
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return datetime.fromisoformat(value).date()
        raise TypeError("Unsupported date value")
