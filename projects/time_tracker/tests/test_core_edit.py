from __future__ import annotations

import datetime as dt

import pytest
from sqlalchemy.orm import Session

from src.core import AlreadyClockedIn, EntryNotFound, InvalidTimeRange, TimeTracker
from src.models import TimeEntry

from .conftest import utcnow


class TestEditEntry:
    def test_edit_entry_updates_start(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        now = utcnow()
        entry = TimeEntry(
            start=now - dt.timedelta(hours=2), end=now - dt.timedelta(hours=1)
        )
        session.add(entry)
        session.commit()
        new_start = now - dt.timedelta(hours=3)
        updated = tracker.edit(entry.id, start=new_start)
        assert updated.start == new_start

    def test_edit_entry_updates_end(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        now = utcnow()
        entry = TimeEntry(
            start=now - dt.timedelta(hours=2), end=now - dt.timedelta(hours=1)
        )
        session.add(entry)
        session.commit()
        new_end = now - dt.timedelta(minutes=30)
        updated = tracker.edit(entry.id, end=new_end)
        assert updated.end == new_end

    def test_edit_entry_updates_note(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        now = utcnow()
        entry = TimeEntry(
            start=now - dt.timedelta(hours=2),
            end=now - dt.timedelta(hours=1),
            note="old",
        )
        session.add(entry)
        session.commit()
        updated = tracker.edit(entry.id, note="new")
        assert updated.note == "new"

    def test_edit_entry_rejects_start_after_end(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        now = utcnow()
        entry = TimeEntry(
            start=now - dt.timedelta(hours=2), end=now - dt.timedelta(hours=1)
        )
        session.add(entry)
        session.commit()
        with pytest.raises(InvalidTimeRange):
            tracker.edit(entry.id, start=now)

    def test_edit_entry_rejects_second_open_entry(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        now = utcnow()
        entry_a = TimeEntry(start=now - dt.timedelta(hours=2), end=None)
        entry_b = TimeEntry(start=now - dt.timedelta(hours=1), end=None)
        session.add_all([entry_a, entry_b])
        session.commit()
        with pytest.raises(AlreadyClockedIn):
            tracker.edit(entry_a.id, note="still open")

    def test_edit_entry_raises_entry_not_found(self, tracker: TimeTracker) -> None:
        with pytest.raises(EntryNotFound):
            tracker.edit(999, note="x")
