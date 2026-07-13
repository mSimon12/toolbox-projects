from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import TimeEntry


class TimeTrackerError(Exception):
    """Base class for domain errors raised by core."""


class AlreadyClockedIn(TimeTrackerError):
    pass


class NotClockedIn(TimeTrackerError):
    pass


@dataclass(frozen=True)
class ReportPeriod:
    start: dt.datetime  # naive UTC, inclusive
    end: dt.datetime  # naive UTC, exclusive


@dataclass
class Status:
    clocked_in: bool
    entry: TimeEntry | None = None
    elapsed: dt.timedelta | None = None


@dataclass
class Report:
    period: ReportPeriod
    total: dt.timedelta
    entries: list[TimeEntry] = field(default_factory=list)


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(tzinfo=None)


def _local_bounds_to_utc(
    local_start: dt.datetime, local_end: dt.datetime
) -> ReportPeriod:
    return ReportPeriod(
        start=local_start.astimezone(dt.UTC).replace(tzinfo=None),
        end=local_end.astimezone(dt.UTC).replace(tzinfo=None),
    )


def _get_open_entry(session: Session) -> TimeEntry | None:
    stmt = select(TimeEntry).where(TimeEntry.end.is_(None))
    return session.scalars(stmt).one_or_none()


def start_entry(session: Session, note: str | None = None) -> TimeEntry:
    if _get_open_entry(session) is not None:
        raise AlreadyClockedIn(
            "An entry is already open; stop it before starting a new one."
        )
    entry = TimeEntry(start=_utcnow(), note=note)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def stop_entry(session: Session, note: str | None = None) -> TimeEntry:
    entry = _get_open_entry(session)
    if entry is None:
        raise NotClockedIn("No open entry to stop.")
    entry.end = _utcnow()
    if note is not None:
        entry.note = note
    session.commit()
    session.refresh(entry)
    return entry


def get_status(session: Session) -> Status:
    entry = _get_open_entry(session)
    if entry is None:
        return Status(clocked_in=False)
    return Status(clocked_in=True, entry=entry, elapsed=_utcnow() - entry.start)


def list_entries(session: Session, limit: int = 20) -> list[TimeEntry]:
    stmt = select(TimeEntry).order_by(TimeEntry.start.desc()).limit(limit)
    return list(session.scalars(stmt).all())


def today_period() -> ReportPeriod:
    local_now = dt.datetime.now().astimezone()
    local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    return _local_bounds_to_utc(local_start, local_start + dt.timedelta(days=1))


def week_period() -> ReportPeriod:
    local_now = dt.datetime.now().astimezone()
    local_start = local_now.replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - dt.timedelta(days=local_now.weekday())
    return _local_bounds_to_utc(local_start, local_start + dt.timedelta(days=7))


def custom_period(start_date: dt.date, end_date: dt.date) -> ReportPeriod:
    tz = dt.datetime.now().astimezone().tzinfo
    local_start = dt.datetime.combine(start_date, dt.time.min, tzinfo=tz)
    local_end = dt.datetime.combine(end_date, dt.time.min, tzinfo=tz) + dt.timedelta(
        days=1
    )
    return _local_bounds_to_utc(local_start, local_end)


def report(session: Session, period: ReportPeriod) -> Report:
    stmt = (
        select(TimeEntry)
        .where(TimeEntry.start >= period.start, TimeEntry.start < period.end)
        .order_by(TimeEntry.start)
    )
    entries = list(session.scalars(stmt).all())
    now = _utcnow()
    total = sum(((e.end or now) - e.start for e in entries), dt.timedelta())
    return Report(period=period, total=total, entries=entries)
