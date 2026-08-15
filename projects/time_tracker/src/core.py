from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.errors import AlreadyClockedIn, EntryExistsForDay, EntryNotFound, InvalidTimeRange, NotClockedIn
from src.models import TimeEntry


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(tzinfo=None)


def _local_bounds_to_utc(local_start: dt.datetime, local_end: dt.datetime) -> ReportPeriod:
    return ReportPeriod(
        start=local_start.astimezone(dt.UTC).replace(tzinfo=None),
        end=local_end.astimezone(dt.UTC).replace(tzinfo=None),
    )


@dataclass(frozen=True)
class ReportPeriod:
    start: dt.datetime  # naive UTC, inclusive
    end: dt.datetime  # naive UTC, exclusive

    @classmethod
    def today(cls) -> ReportPeriod:
        local_now = dt.datetime.now().astimezone()
        local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        return _local_bounds_to_utc(local_start, local_start + dt.timedelta(days=1))

    @classmethod
    def this_week(cls) -> ReportPeriod:
        local_now = dt.datetime.now().astimezone()
        local_start = local_now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - dt.timedelta(days=local_now.weekday())
        return _local_bounds_to_utc(local_start, local_start + dt.timedelta(days=7))

    @classmethod
    def custom(cls, start_date: dt.date, end_date: dt.date) -> ReportPeriod:
        tz = dt.datetime.now().astimezone().tzinfo
        local_start = dt.datetime.combine(start_date, dt.time.min, tzinfo=tz)
        local_end = dt.datetime.combine(
            end_date, dt.time.min, tzinfo=tz
        ) + dt.timedelta(days=1)
        return _local_bounds_to_utc(local_start, local_end)


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


@dataclass
class PauseResult:
    applied: bool
    entry: TimeEntry | None = None
    new_entry: TimeEntry | None = None


class TimeTracker:
    """Business logic for tracking work hours, backed by a SQLAlchemy Session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def _get_open_entry(self) -> TimeEntry | None:
        stmt = select(TimeEntry).where(TimeEntry.end.is_(None))
        return self.session.scalars(stmt).one_or_none()

    def _get_entry(self, entry_id: int) -> TimeEntry:
        entry = self.session.get(TimeEntry, entry_id)
        if entry is None:
            raise EntryNotFound(f"No entry with id {entry_id}.")
        return entry

    def start(self, note: str | None = None) -> TimeEntry:
        if self._get_open_entry() is not None:
            raise AlreadyClockedIn(
                "An entry is already open; stop it before starting a new one."
            )
        entry = TimeEntry(start=_utcnow(), note=note)
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def stop(self, note: str | None = None) -> TimeEntry:
        entry = self._get_open_entry()
        if entry is None:
            raise NotClockedIn("No open entry to stop.")
        entry.end = _utcnow()
        if note is not None:
            entry.note = note
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def status(self) -> Status:
        entry = self._get_open_entry()
        if entry is None:
            return Status(clocked_in=False)
        return Status(clocked_in=True, entry=entry, elapsed=_utcnow() - entry.start)

    def list_entries(self, limit: int = 20) -> list[TimeEntry]:
        stmt = select(TimeEntry).order_by(TimeEntry.start.desc()).limit(limit)
        return list(self.session.scalars(stmt).all())

    def log(self, day: dt.date, start_time: dt.time, end_time: dt.time,  note: str | None = None, force: bool = False) -> TimeEntry:
        tz = dt.datetime.now().astimezone().tzinfo
        local_day_start = dt.datetime.combine(day, dt.time.min, tzinfo=tz)
        local_day_end = local_day_start + dt.timedelta(days=1)
        day_bounds = _local_bounds_to_utc(local_day_start, local_day_end)

        if not force:
            stmt = select(TimeEntry).where(
                TimeEntry.start >= day_bounds.start, TimeEntry.start < day_bounds.end
            )
            if self.session.scalars(stmt).first() is not None:
                raise EntryExistsForDay(
                    f"An entry already starts on {day.isoformat()}; "
                    "pass force=True to override."
                )

        local_start = dt.datetime.combine(day, start_time, tzinfo=tz)
        local_end = dt.datetime.combine(day, end_time, tzinfo=tz)
        if local_end <= local_start:
            raise InvalidTimeRange("Entry start must be before end.")
        bounds = _local_bounds_to_utc(local_start, local_end)

        entry = TimeEntry(start=bounds.start, end=bounds.end, note=note)
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def edit(self, entry_id: int, *, start: dt.datetime | None = None, end: dt.datetime | None = None, note: str | None = None) -> TimeEntry:
        entry = self._get_entry(entry_id)

        new_start = start if start is not None else entry.start
        new_end = end if end is not None else entry.end
        new_note = note if note is not None else entry.note

        if new_end is not None and new_start >= new_end:
            raise InvalidTimeRange("Entry start must be before end.")

        if new_end is None:
            stmt = select(TimeEntry).where(
                TimeEntry.end.is_(None), TimeEntry.id != entry_id
            )
            if self.session.scalars(stmt).first() is not None:
                raise AlreadyClockedIn(
                    "Another entry is already open; "
                    "stop it before leaving this one open."
                )

        entry.start = new_start
        entry.end = new_end
        entry.note = new_note
        self.session.commit()
        self.session.refresh(entry)
        return entry

    def delete(self, entry_id: int) -> None:
        entry = self._get_entry(entry_id)
        self.session.delete(entry)
        self.session.commit()

    def pause(self, pause_start: dt.datetime, pause_end: dt.datetime) -> PauseResult:
        if pause_start >= pause_end:
            raise InvalidTimeRange("Pause start must be before pause end.")

        stmt = select(TimeEntry).where(
            TimeEntry.end.is_not(None),
            TimeEntry.start < pause_start,
            TimeEntry.end > pause_end,
        )
        matches = list(self.session.scalars(stmt).all())
        if len(matches) != 1:
            return PauseResult(applied=False)

        entry = matches[0]
        new_entry = TimeEntry(start=pause_end, end=entry.end, note=entry.note)
        entry.end = pause_start
        self.session.add(new_entry)
        self.session.commit()
        self.session.refresh(entry)
        self.session.refresh(new_entry)
        return PauseResult(applied=True, entry=entry, new_entry=new_entry)

    def report(self, period: ReportPeriod) -> Report:
        stmt = (
            select(TimeEntry)
            .where(TimeEntry.start >= period.start, TimeEntry.start < period.end)
            .order_by(TimeEntry.start)
        )
        entries = list(self.session.scalars(stmt).all())
        now = _utcnow()
        total = sum(((e.end or now) - e.start for e in entries), dt.timedelta())
        return Report(period=period, total=total, entries=entries)
