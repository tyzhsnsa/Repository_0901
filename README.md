# Task Manager CLI

This repository provides a small, file-backed task manager that can be used from the command line or imported as a Python module. The tool keeps a JSON database of tasks and offers helpers for listing, completing, and filtering tasks that are due soon.

## Features

- Persistent JSON storage with automatic file creation.
- Simple command line interface for adding, listing, and completing tasks.
- Upcoming-task filter to focus on tasks that are due within a chosen number of days.
- Library API exposed through the `task_manager` package for reuse in other scripts.
- Optional category labels and attachment paths (useful for associating images or other assets).
- Helper to schedule daily devotional posts that combine scripture, a daily message, and an optional image.

## Usage

```bash
$ task-manager add "Buy groceries" --due 2025-10-31
$ task-manager list
$ task-manager upcoming --days 3
$ task-manager devotional --scripture "John 3:16" --message "Daily encouragement" --days 3 --image path/to/image.png
```

The storage file defaults to `.tasks.json` in the current working directory. You can override the location with the `--storage` option on any command.

## Development

Install dependencies (only `pytest` for tests) and run the test suite:

```bash
pip install -r requirements-dev.txt
pytest
```
