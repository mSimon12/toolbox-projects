# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

`time_tracker` — a personal work-hours tracker. Starts as a shell CLI, must stay
upgradeable to a GUI (customtkinter) or web layer (FastAPI) **without touching
the data or business-logic layers**. That upgrade path is the single most
important architectural constraint.

## Golden rules

1. **Strict layer separation.** The interface (CLI now, GUI later) is a thin
   shell over `core`. `core` contains all business logic and returns plain
   Python data (dataclasses / model instances), never printed output and never
   CLI objects. A new frontend must require zero changes in `core` or `db`.
2. **`core` never imports `cli`.** Dependencies point one direction:
   `cli → core → db → models`. Never the reverse.
3. **No printing or `typer.echo` outside `cli.py`.** `core` returns data; the
   CLI formats it.
4. **Sync only.** This is a local single-user tool. Do not introduce async.
5. Keep dependencies minimal. Nothing beyond the stack below without asking.

## Stack

- Python 3.12+
- SQLAlchemy 2.0 (typed `Mapped` / `mapped_column`, sync `Session`)
- SQLite (single file, path from config/env, default `~/.time_tracker/time_tracker.db`)
- Typer for the CLI
- `uv` for env + dependency management
- pytest for tests
- ruff + black for lint/format

## Layout

```
time_tracker/
├── time_tracker/
│   ├── __init__.py
│   ├── models.py     # SQLAlchemy 2.0 ORM models (Mapped/mapped_column)
│   ├── db.py         # engine, session factory, init_db()
│   ├── core.py       # business logic; pure functions taking a Session
│   └── cli.py        # Typer app; the ONLY layer that prints
├── tests/
├── pyproject.toml
└── CLAUDE.md
```

## Data model (starting point)

`TimeEntry`: `id` (PK), `start` (datetime, required), `end` (datetime,
nullable — null means clocked-in), `note` (str, nullable).

An "open" entry is one with `end IS NULL`. There should be at most one open
entry at a time; `start` must reject a new one if an open entry already exists,
and `stop` must fail clearly if none is open.

## CLI commands (v1)

- `time_tracker start [--note TEXT]` — open a new entry (error if one is open)
- `time_tracker stop [--note TEXT]` — close the open entry (error if none open)
- `time_tracker status` — show whether clocked in, and elapsed time if so
- `time_tracker report [--today|--week|--from DATE --to DATE]` — total hours + entries
- `time_tracker list [--limit N]` — recent entries

## Core API shape

`core.py` exposes functions like `start_entry(session, note=None) -> TimeEntry`,
`stop_entry(session, note=None) -> TimeEntry`, `get_status(session) -> Status`,
`report(session, period) -> Report`. They take a `Session`, raise domain errors
(e.g. `AlreadyClockedIn`, `NotClockedIn`) defined in `core`, and return data
objects. The CLI catches those errors and renders friendly messages.

## Conventions

- Store datetimes in UTC; convert to local only for display in `cli.py`.
- Custom exceptions live in `core.py` and are caught only in `cli.py`.
- Type hints everywhere; code must pass `ruff check` and `black --check`.
- Tests cover `core` against an in-memory SQLite DB and do **not** go through
  the CLI for logic assertions.

## Definition of done for v1

Working `start/stop/status/report/list`, `core` fully unit-tested without the
CLI, clean ruff + black, and a short README with install (`uv`) and usage.

## When unsure

If a change would blur the layer boundaries or add a dependency, stop and ask
rather than guessing.