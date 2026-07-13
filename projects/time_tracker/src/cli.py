from __future__ import annotations

import datetime as dt
from collections.abc import Iterator
from contextlib import contextmanager

import typer
from sqlalchemy.orm import Session

from src import core, db

app = typer.Typer(help="Personal work-hours tracker.")


@contextmanager
def _session() -> Iterator[Session]:
    db.init_db()
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _to_local_str(value: dt.datetime, fmt: str = "%Y-%m-%d %H:%M") -> str:
    return value.replace(tzinfo=dt.UTC).astimezone().strftime(fmt)


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
    with _session() as session:
        try:
            entry = core.start_entry(session, note=note)
        except core.AlreadyClockedIn as exc:
            _fail(str(exc))
    typer.echo(f"Clocked in at {_to_local_str(entry.start)}.")


@app.command()
def stop(
    note: str | None = typer.Option(None, help="Optional note for this entry."),
) -> None:
    """Close the open entry (error if none open)."""
    with _session() as session:
        try:
            entry = core.stop_entry(session, note=note)
        except core.NotClockedIn as exc:
            _fail(str(exc))
    elapsed = entry.end - entry.start
    typer.echo(
        f"Clocked out at {_to_local_str(entry.end)} ({_format_timedelta(elapsed)})."
    )


@app.command()
def status() -> None:
    """Show whether clocked in, and elapsed time if so."""
    with _session() as session:
        result = core.get_status(session)
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
        period = core.today_period()
    elif week:
        period = core.week_period()
    else:
        if not (from_ and to):
            _fail("Both --from and --to are required together.")
        try:
            start_date = dt.date.fromisoformat(from_)
            end_date = dt.date.fromisoformat(to)
        except ValueError as exc:
            _fail(f"Invalid date: {exc}")
        period = core.custom_period(start_date, end_date)

    with _session() as session:
        result = core.report(session, period)

    typer.echo(f"Total: {_format_timedelta(result.total)}")
    for entry in result.entries:
        typer.echo(_format_entry(entry))


@app.command(name="list")
def list_entries(
    limit: int = typer.Option(20, help="Number of recent entries to show."),
) -> None:
    """Show recent entries."""
    with _session() as session:
        entries = core.list_entries(session, limit=limit)
    if not entries:
        typer.echo("No entries yet.")
        return
    for entry in entries:
        typer.echo(f"{entry.id:>4}{_format_entry(entry)}")


if __name__ == "__main__":
    app()
