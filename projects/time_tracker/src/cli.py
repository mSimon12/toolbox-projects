from __future__ import annotations

import datetime as dt
from collections.abc import Iterator
from contextlib import contextmanager

import typer
from sqlalchemy.orm import Session

from src import core, db, errors

app = typer.Typer(help="Personal work-hours tracker.")


@contextmanager
def _tracker() -> Iterator[core.TimeTracker]:
    db.init_db()
    session: Session = db.SessionLocal()
    try:
        yield core.TimeTracker(session)
    finally:
        session.close()


def _to_local_str(value: dt.datetime, fmt: str = "%Y-%m-%d %H:%M") -> str:
    return value.replace(tzinfo=dt.UTC).astimezone().strftime(fmt)


def _local_str_to_utc(value: str) -> dt.datetime:
    try:
        naive_local = dt.datetime.strptime(value, "%Y-%m-%d %H:%M")
    except ValueError as exc:
        _fail(f"Invalid time '{value}': expected format YYYY-MM-DD HH:MM ({exc}).")
    return naive_local.astimezone(dt.UTC).replace(tzinfo=None)


def _parse_time(value: str) -> dt.time:
    try:
        return dt.datetime.strptime(value, "%H:%M").time()
    except ValueError as exc:
        _fail(f"Invalid time '{value}': expected format HH:MM ({exc}).")


def _format_timedelta(td: dt.timedelta) -> str:
    total_minutes = int(td.total_seconds() // 60)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}h {minutes:02d}m"


def _format_entry(entry) -> str:
    end_str = _to_local_str(entry.end) if entry.end else "open"
    note = f" — {entry.note}" if entry.note else ""
    return f"  {_to_local_str(entry.start)} -> {end_str}{note}"


def _fail(message: str) -> None:
    typer.secho(message, fg=typer.colors.RED, err=True)
    raise typer.Exit(code=1)


@app.command()
def start(
    note: str | None = typer.Option(None, help="Optional note for this entry."),
) -> None:
    """Open a new entry (error if one is already open)."""
    with _tracker() as tracker:
        try:
            entry = tracker.start(note=note)
        except errors.AlreadyClockedIn as exc:
            _fail(str(exc))
    typer.echo(f"Clocked in at {_to_local_str(entry.start)}.")


@app.command()
def stop(
    note: str | None = typer.Option(None, help="Optional note for this entry."),
) -> None:
    """Close the open entry (error if none open)."""
    with _tracker() as tracker:
        try:
            entry = tracker.stop(note=note)
        except errors.NotClockedIn as exc:
            _fail(str(exc))
    elapsed = entry.end - entry.start
    typer.echo(
        f"Clocked out at {_to_local_str(entry.end)} ({_format_timedelta(elapsed)})."
    )


@app.command()
def status() -> None:
    """Show whether clocked in, and elapsed time if so."""
    with _tracker() as tracker:
        result = tracker.status()
    if not result.clocked_in:
        typer.echo("Not clocked in.")
        return
    typer.echo(
        f"Clocked in since {_to_local_str(result.entry.start)} "
        f"({_format_timedelta(result.elapsed)} elapsed)."
    )


@app.command()
def report(
    today: bool = typer.Option(False, "--today", help="Report for today."),
    week: bool = typer.Option(False, "--week", help="Report for this week."),
    from_: str | None = typer.Option(
        None, "--from", help="Start date (YYYY-MM-DD, inclusive)."
    ),
    to: str | None = typer.Option(
        None, "--to", help="End date (YYYY-MM-DD, inclusive)."
    ),
) -> None:
    """Show total hours and entries for a period."""
    flags_used = sum([today, week, bool(from_ or to)])
    if flags_used == 0:
        today = True
    elif flags_used > 1:
        _fail("Choose only one of --today, --week, or --from/--to.")

    if today:
        period = core.ReportPeriod.today()
    elif week:
        period = core.ReportPeriod.this_week()
    else:
        if not (from_ and to):
            _fail("Both --from and --to are required together.")
        try:
            start_date = dt.date.fromisoformat(from_)
            end_date = dt.date.fromisoformat(to)
        except ValueError as exc:
            _fail(f"Invalid date: {exc}")
        period = core.ReportPeriod.custom(start_date, end_date)

    with _tracker() as tracker:
        result = tracker.report(period)

    typer.echo(f"Total: {_format_timedelta(result.total)}")
    for entry in result.entries:
        typer.echo(_format_entry(entry))


@app.command(name="list")
def list_entries(
    limit: int = typer.Option(20, help="Number of recent entries to show."),
) -> None:
    """Show recent entries."""
    with _tracker() as tracker:
        entries = tracker.list_entries(limit=limit)
    if not entries:
        typer.echo("No entries yet.")
        return
    for entry in entries:
        typer.echo(f"{entry.id:>4}{_format_entry(entry)}")


@app.command(name="log")
def log_entry(
    day: str = typer.Option(..., "--day", help='Day to log, "YYYY-MM-DD" or "today".'),
    start: str = typer.Option(..., "--start", help="Start time, HH:MM local."),
    end: str = typer.Option(..., "--end", help="End time, HH:MM local."),
    note: str | None = typer.Option(None, help="Optional note for this entry."),
    force: bool = typer.Option(
        False, "--force", help="Override an existing entry for that day."
    ),
) -> None:
    """Add a completed entry for a past day, given explicit start and end times."""
    if day.strip().lower() == "today":
        log_date = dt.date.today()
    else:
        try:
            log_date = dt.date.fromisoformat(day)
        except ValueError as exc:
            _fail(f"Invalid day '{day}': {exc}")

    start_time = _parse_time(start)
    end_time = _parse_time(end)

    with _tracker() as tracker:
        try:
            entry = tracker.log(log_date, start_time, end_time, note=note, force=force)
        except (errors.EntryExistsForDay, errors.InvalidTimeRange) as exc:
            _fail(str(exc))
    typer.echo(f"Logged entry {entry.id}:{_format_entry(entry)}")


@app.command()
def edit(
    entry_id: int = typer.Option(..., "--id", help="Entry id to edit."),
    start: str | None = typer.Option(
        None, "--start", help='New start, "YYYY-MM-DD HH:MM" local.'
    ),
    end: str | None = typer.Option(
        None, "--end", help='New end, "YYYY-MM-DD HH:MM" local.'
    ),
    note: str | None = typer.Option(None, "--note", help="New note."),
) -> None:
    """Update fields on an existing entry."""
    new_start = _local_str_to_utc(start) if start is not None else None
    new_end = _local_str_to_utc(end) if end is not None else None

    with _tracker() as tracker:
        try:
            entry = tracker.edit(entry_id, start=new_start, end=new_end, note=note)
        except (
            errors.EntryNotFound,
            errors.InvalidTimeRange,
            errors.AlreadyClockedIn,
        ) as exc:
            _fail(str(exc))
    typer.echo(f"Updated entry {entry.id}:{_format_entry(entry)}")


@app.command()
def delete(
    entry_id: int = typer.Option(..., "--id", help="Entry id to delete."),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmation prompt."),
) -> None:
    """Remove an entry."""
    if not yes and not typer.confirm(f"Delete entry {entry_id}?"):
        typer.echo("Aborted.")
        raise typer.Exit(code=0)

    with _tracker() as tracker:
        try:
            tracker.delete(entry_id)
        except errors.EntryNotFound as exc:
            _fail(str(exc))
    typer.echo(f"Deleted entry {entry_id}.")


@app.command()
def pause(
    start: str = typer.Option(
        ..., "--start", help='Pause start, "YYYY-MM-DD HH:MM" local.'
    ),
    end: str = typer.Option(..., "--end", help='Pause end, "YYYY-MM-DD HH:MM" local.'),
) -> None:
    """Split the entry that strictly contains this window, excluding the gap."""
    pause_start = _local_str_to_utc(start)
    pause_end = _local_str_to_utc(end)

    with _tracker() as tracker:
        try:
            result = tracker.pause(pause_start, pause_end)
        except errors.InvalidTimeRange as exc:
            _fail(str(exc))

    if not result.applied:
        typer.echo("No entry strictly contains that window; ignored.")
        return
    typer.echo(
        f"Pause applied: entry {result.entry.id}:{_format_entry(result.entry)}\n"
        f"            new entry {result.new_entry.id}:"
        f"{_format_entry(result.new_entry)}"
    )


if __name__ == "__main__":
    app()
