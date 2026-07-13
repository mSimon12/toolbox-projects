# Time Tracker

A personal work-hours tracker. Clock in, clock out, and see reports from the
command line. Built with a strict layer separation so a GUI or web frontend
can be added later without touching the data or business-logic layers.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for environment and dependency management

## Install

```bash
uv sync
```

This creates `.venv/` and installs runtime + dev dependencies (SQLAlchemy,
Typer, pytest, ruff, black) from `uv.lock`.

## Usage

Run via `uv run`, or activate `.venv` and use the `time-tracker` script
directly.

```bash
uv run time-tracker start [--note TEXT]     # open a new entry (error if one is already open)
uv run time-tracker stop [--note TEXT]      # close the open entry (error if none open)
uv run time-tracker status                  # show whether clocked in, and elapsed time
uv run time-tracker list [--limit N]        # show recent entries (default 20)
uv run time-tracker report [--today | --week | --from DATE --to DATE]
                                             # total hours + entries for a period
                                             # (defaults to --today if no flag given)
uv run time-tracker log --day DAY --start HH:MM --end HH:MM [--note TEXT] [--force]
                                             # add a completed entry for a past day; DAY is
                                             # YYYY-MM-DD or "today", start/end are local HH:MM
                                             # (error if that day already has an entry, unless --force)
uv run time-tracker edit --id ID [--start "YYYY-MM-DD HH:MM"] [--end "YYYY-MM-DD HH:MM"] [--note TEXT]
                                             # update one or more fields on an existing entry
uv run time-tracker delete --id ID [--yes]  # remove an entry (prompts for confirmation unless --yes)
uv run time-tracker pause --start "YYYY-MM-DD HH:MM" --end "YYYY-MM-DD HH:MM"
                                             # retroactively split the single entry that strictly
                                             # contains this window into two rows, excluding the gap;
                                             # ignored (no-op) if no entry strictly contains the window
```

Dates for `--from`/`--to` use `YYYY-MM-DD` and are inclusive on both ends.
Times for `log --start`/`--end` use local time in `HH:MM` format (paired with
`--day`). Times for `edit --start`/`--end` and `pause --start`/`--end` use
local time in `YYYY-MM-DD HH:MM` format.

### Example

```bash
$ uv run time-tracker start --note "writing docs"
Clocked in at 2026-07-13 18:48.

$ uv run time-tracker status
Clocked in since 2026-07-13 18:48 (0h 12m elapsed).

$ uv run time-tracker stop
Clocked out at 2026-07-13 19:05 (0h 17m).

$ uv run time-tracker report --today
Total: 0h 17m
  2026-07-13 18:48 -> 2026-07-13 19:05 — writing docs
```

### Editing past entries

```bash
$ uv run time-tracker log --day 2026-07-10 --start 09:00 --end 15:00 --note "conference"
Logged entry 1:  2026-07-10 09:00 -> 2026-07-10 15:00 — conference

$ uv run time-tracker edit --id 1 --end "2026-07-10 16:00"
Updated entry 1:  2026-07-10 09:00 -> 2026-07-10 16:00 — conference

$ uv run time-tracker pause --start "2026-07-10 12:00" --end "2026-07-10 13:00"
Pause applied: entry 1:  2026-07-10 09:00 -> 2026-07-10 12:00 — conference
            new entry 2:  2026-07-10 13:00 -> 2026-07-10 16:00 — conference

$ uv run time-tracker delete --id 2 --yes
Deleted entry 2.
```

`pause` only splits an entry when the window falls **strictly inside** it —
touching a boundary, spanning two entries, or targeting the still-open entry
all leave the data untouched and print that the pause was ignored.

## Configuration

The SQLite database defaults to `~/.time_tracker/time_tracker.db`. Override
it with an environment variable, e.g. for a scratch DB or tests:

```bash
export TIME_TRACKER_DB=/path/to/other.db
```

## Project layout

```
time_tracker/
├── src/
│   ├── __init__.py
│   ├── models.py   # SQLAlchemy 2.0 ORM models (Mapped/mapped_column)
│   ├── db.py        # engine, session factory, init_db()
│   ├── core.py       # business logic; pure functions taking a Session
│   └── cli.py        # Typer app; the only layer that prints
├── tests/
│   ├── conftest.py   # in-memory SQLite `session` fixture
│   └── test_core.py  # core tests (no CLI involved)
├── pyproject.toml
├── uv.lock
└── CLAUDE.md          # guidance for AI-assisted development in this repo
```

## Architecture

Dependencies point one direction: `cli → core → db → models`. `core` never
imports `cli`.

- **`core.py`** contains all business logic. Its functions take a SQLAlchemy
  `Session` and return plain data (dataclasses or model instances) — never
  printed output, never CLI-specific objects. Domain errors
  (`AlreadyClockedIn`, `NotClockedIn`) are raised here and caught only in
  `cli.py`.
- **`cli.py`** is a thin Typer shell over `core`. It's the only module that
  prints, and the only place that catches domain exceptions to render
  friendly messages.
- **`db.py`** owns the engine, session factory (`SessionLocal`), and
  `init_db()`, which creates tables if needed.
- **`models.py`** defines the ORM schema. `TimeEntry` has `id`, `start`
  (required), `end` (nullable — null means clocked-in), and `note`
  (nullable). At most one entry may be open (`end IS NULL`) at a time.
- Datetimes are stored as naive UTC values; `cli.py` converts to local time
  only for display.
- Sync only — no async, since this is a local single-user tool.

This separation means a future GUI (e.g. customtkinter) or web layer (e.g.
FastAPI) can be built as a new frontend module that imports `core` directly,
with zero changes required in `core` or `db`.

## Development

```bash
uv run pytest              # run tests
uv run ruff check .        # lint
uv run black .              # format (or --check to verify without writing)
```

Tests exercise `core` directly against an in-memory SQLite database (see
`tests/conftest.py`) and do not go through the CLI for logic assertions.

See `CLAUDE.md` for the full set of conventions and constraints this project
follows.
