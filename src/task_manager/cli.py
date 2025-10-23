"""Command line interface for the task manager."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from .manager import Task, TaskManager


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="File-backed task manager")
    parser.add_argument(
        "--storage",
        type=Path,
        default=Path.cwd() / ".tasks.json",
        help="Path to the JSON file used to store tasks (default: .tasks.json in current directory)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Title of the task")
    add_parser.add_argument(
        "--description",
        "-d",
        default="",
        help="Optional task description",
    )
    add_parser.add_argument(
        "--due",
        help="Due date in ISO format (YYYY-MM-DD). Leave empty for no due date.",
    )
    add_parser.add_argument(
        "--category",
        help="Optional category label for the task",
    )
    add_parser.add_argument(
        "--attachment",
        help="Path to an attachment (for example an image) associated with the task",
    )

    list_parser = subparsers.add_parser("list", help="List stored tasks")
    list_parser.add_argument(
        "--pending-only",
        action="store_true",
        help="Only show tasks that have not been completed",
    )

    complete_parser = subparsers.add_parser("complete", help="Mark a task as complete or incomplete")
    complete_parser.add_argument("task_id", type=int, help="Identifier of the task")
    complete_parser.add_argument(
        "--incomplete",
        action="store_true",
        help="Mark the task as incomplete instead of complete",
    )

    upcoming_parser = subparsers.add_parser("upcoming", help="Show tasks due within a number of days")
    upcoming_parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to look ahead (default: 7)",
    )
    upcoming_parser.add_argument(
        "--include-completed",
        action="store_true",
        help="Include completed tasks in the results",
    )

    devotional_parser = subparsers.add_parser(
        "devotional",
        help="Schedule daily devotional posts with scripture, message, and optional image",
    )
    devotional_parser.add_argument(
        "--start",
        help="Start date in ISO format for the first devotional task (defaults to today)",
    )
    devotional_parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of consecutive days to schedule (default: 1)",
    )
    devotional_parser.add_argument(
        "--title-template",
        default="デボーション投稿 ({date})",
        help="Template for the generated task titles. Use {date} for the ISO date.",
    )
    devotional_parser.add_argument(
        "--scripture",
        required=True,
        help="Template for the scripture text. Use {date} for the ISO date.",
    )
    devotional_parser.add_argument(
        "--message",
        required=True,
        help="Template for the day's message. Use {date} for the ISO date.",
    )
    devotional_parser.add_argument(
        "--image",
        help="Optional path to an image to attach to each devotional task",
    )
    devotional_parser.add_argument(
        "--category",
        default="devotional",
        help="Optional category label applied to devotional tasks (default: devotional)",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    manager = TaskManager(args.storage)

    if args.command == "add":
        task = manager.add_task(
            args.title,
            args.description,
            due_date=args.due,
            category=args.category,
            attachment_path=args.attachment,
        )
        print(f"Created task #{task.id}: {task.title}")
        return 0

    if args.command == "list":
        tasks = manager.list_tasks(include_completed=not args.pending_only)
        _print_tasks(tasks)
        return 0

    if args.command == "complete":
        task = manager.complete_task(args.task_id, completed=not args.incomplete)
        status = "complete" if task.completed else "incomplete"
        print(f"Marked task #{task.id} as {status}")
        return 0

    if args.command == "upcoming":
        tasks = manager.upcoming_tasks(
            within_days=args.days,
            include_completed=args.include_completed,
        )
        if not tasks:
            print("No tasks due in the selected window")
        else:
            print(f"Tasks due in the next {args.days} day(s):")
            _print_tasks(tasks)
        return 0

    if args.command == "devotional":
        tasks = manager.schedule_devotional_posts(
            start=args.start,
            days=args.days,
            title_template=args.title_template,
            scripture_template=args.scripture,
            message_template=args.message,
            image_path=args.image,
            category=args.category,
        )
        print(f"Scheduled {len(tasks)} devotional task(s)")
        return 0

    parser.error("Unsupported command")
    return 2


def _print_tasks(tasks: Iterable[Task]) -> None:
    for task in tasks:
        due = task.due_date.isoformat() if task.due_date else "(no due date)"
        status = "✓" if task.completed else "✗"
        print(f"[{status}] #{task.id} {task.title} - due {due}")
        details = []
        if task.category:
            details.append(f"category: {task.category}")
        if task.attachment_path:
            details.append(f"attachment: {task.attachment_path}")
        if details:
            print(f"    ({'; '.join(details)})")
        if task.description:
            print(f"    {task.description}")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
