# Task Manager CLI

This repository provides a small, file-backed task manager that can be used from the command line or imported as a Python module. The tool keeps a JSON database of tasks and offers helpers for listing, completing, and filtering tasks that are due soon.

## Features

- Persistent JSON storage with automatic file creation.
- Simple command line interface for adding, listing, and completing tasks.
- Upcoming-task filter to focus on tasks that are due within a chosen number of days.
- Library API exposed through the `task_manager` package for reuse in other scripts.

## Usage

```bash
$ task-manager add "Buy groceries" --due 2025-10-31
$ task-manager list
$ task-manager upcoming --days 3
```

The storage file defaults to `.tasks.json` in the current working directory. You can override the location with the `--storage` option on any command.

## Development

Install dependencies (only `pytest` for tests) and run the test suite:

```bash
pip install -r requirements-dev.txt
pytest
```
