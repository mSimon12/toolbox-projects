# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project

`time_tracker` — a personal work-hours tracker. Starts as a shell CLI, must stay
upgradeable to a GUI (customtkinter) or web layer (FastAPI) **without touching
the data or business-logic layers**. That upgrade path is the single most
important architectural constraint.

Live tracking is deliberately minimal: `start`/`stop` only, always anchored to
"now." There is no live pause/resume and no separate `Break` table. Breaks are
handled retroactively — `pause` splits one `TimeEntry` row into two, and the
gap between them is simply never covered by any row.

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
├── src/
│   ├── __init__.py
│   ├── models.py     # SQLAlchemy 2.0 ORM models (Mapped/mapped_column)
│   ├── db.py         # engine, session factory, init_db()
│   ├── errors.py     # domain exceptions raised by core
│   ├── core.py       # business logic; TimeTracker service class wrapping a Session
│   └── cli.py        # Typer app; the ONLY layer that prints
├── tests/
├── pyproject.toml
└── CLAUDE.md
```

## Data model

`TimeEntry`: `id` (PK), `start` (datetime, required), `end` (datetime,
nullable — null means clocked-in), `note` (str, nullable).

An "open" entry is one with `end IS NULL`. There should be at most one open
entry at a time; `start`/`log` must reject creating a new one while one is
open, and `stop` must fail clearly if none is open.

There is no `Break` table. A break is represented purely as the gap between
two adjacent `TimeEntry` rows — produced by `pause` splitting one entry into
two. `report` sums each entry's own span, so any such gap is naturally
excluded from totals without special-casing.

v1 does not validate overlapping entries across unrelated rows — only the
single-open-entry invariant is enforced.

## CLI commands

- `time_tracker start [--note TEXT]` — open a new entry now (error if one is open)
- `time_tracker stop [--note TEXT]` — close the open entry now (error if none open)
- `time_tracker status` — show whether clocked in, and elapsed time if so
- `time_tracker report [--today|--week|--from DATE --to DATE]` — total hours + entries
- `time_tracker list [--limit N]` — recent entries, including their IDs
- `time_tracker log --day DAY --start HH:MM --end HH:MM [--note TEXT] [--force]`
  — add a completed entry for a past day (not live; both ends given up front),
  `DAY` is `YYYY-MM-DD` or "today"
- `time_tracker edit ID [--start "YYYY-MM-DD HH:MM"] [--end "YYYY-MM-DD HH:MM"] [--note TEXT]`
  — update fields on an existing entry
- `time_tracker delete ID` — remove an entry
- `time_tracker pause ID --start "YYYY-MM-DD HH:MM" --end "YYYY-MM-DD HH:MM" [--note TEXT]`
  — retroactively split entry `ID` into two rows around a break: the original
  entry's `end` is shortened to the pause start, and a new entry is created
  from the pause end to the original `end` (or left open, if the original was
  still open)

## Core API shape

`core.py` exposes a `TimeTracker` service class, constructed with a `Session`
and holding it for the lifetime of the instance:

- `TimeTracker(session)`
- `.start(note=None) -> TimeEntry`
- `.stop(note=None) -> TimeEntry`
- `.status() -> Status`
- `.report(period) -> Report`
- `.list_entries(limit=20) -> list[TimeEntry]`
- `.log(day, start_time, end_time, note=None, force=False) -> TimeEntry`
- `.edit(entry_id, *, start=None, end=None, note=None) -> TimeEntry`
- `.delete(entry_id) -> None`
- `.pause(pause_start, pause_end) -> PauseResult`
  — splits whichever entry strictly contains the window; `PauseResult.applied`
  is `False` if none (or more than one) does

`ReportPeriod` exposes period construction as classmethods:
`ReportPeriod.today()`, `ReportPeriod.this_week()`,
`ReportPeriod.custom(start_date, end_date)`.

Methods raise domain errors (`AlreadyClockedIn`, `NotClockedIn`,
`EntryNotFound`, `InvalidTimeRange`, `EntryExistsForDay`) defined in
`errors.py`. The CLI instantiates one `TimeTracker` per command invocation via
`core.TimeTracker(session)`, catches those errors as `errors.AlreadyClockedIn`
etc., and renders friendly messages — it imports the modules (`from src
import core, db, errors`) rather than individual names.

## Conventions

- Store datetimes in UTC; convert to local only for display in `cli.py`.
- User-facing time inputs are parsed in `cli.py`: `log --start`/`--end` take
  local `HH:MM` (paired with `--day`) and are passed into `core` as
  `dt.time` values alongside the `dt.date`; `edit`/`pause` take local
  `YYYY-MM-DD HH:MM` strings, converted to naive UTC `dt.datetime` before
  being passed into `core`. Raw strings never cross into `core`.
- Custom exceptions live in `errors.py`, imported directly by both `core.py`
  (to raise them) and `cli.py` (to catch them).
- Type hints everywhere; code must pass `ruff check` and `black --check`.
- Tests cover `core` against an in-memory SQLite DB and do **not** go through
  the CLI for logic assertions.

## Definition of done for v1

Working `start/stop/status/report/list/log/edit/delete/pause`, `core` fully
unit-tested without the CLI, clean ruff + black, and a short README with
install (`uv`) and usage.

## When unsure

If a change would blur the layer boundaries or add a dependency, stop and ask
rather than guessing.
