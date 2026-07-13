from __future__ import annotations

import datetime as dt

import pytest
from sqlalchemy.orm import Session

from src.core import InvalidTimeRange, TimeTracker
from src.models import TimeEntry

from .conftest import utcnow


class TestInsertPause:
    def test_strictly_inside_splits_into_two_rows(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        start = utcnow()
        entry = TimeEntry(start=start, end=start + dt.timedelta(hours=2), note="work")
        session.add(entry)
        session.commit()

        pause_start = start + dt.timedelta(minutes=30)
        pause_end = start + dt.timedelta(minutes=45)
        result = tracker.pause(pause_start, pause_end)

        assert result.applied is True
        assert result.entry.id == entry.id
        assert result.entry.end == pause_start
        assert result.new_entry.start == pause_end
        assert result.new_entry.end == start + dt.timedelta(hours=2)
        assert result.new_entry.note == "work"
        assert len(tracker.list_entries()) == 2

    def test_out_of_range_ignored(self, session: Session, tracker: TimeTracker) -> None:
        start = utcnow()
        entry = TimeEntry(start=start, end=start + dt.timedelta(hours=1))
        session.add(entry)
        session.commit()

        result = tracker.pause(
            start - dt.timedelta(hours=2), start - dt.timedelta(hours=1)
        )

        assert result.applied is False
        assert len(tracker.list_entries()) == 1
        assert entry.end == start + dt.timedelta(hours=1)

    def test_touching_start_boundary_ignored(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        start = utcnow()
        entry = TimeEntry(start=start, end=start + dt.timedelta(hours=1))
        session.add(entry)
        session.commit()

        result = tracker.pause(start, start + dt.timedelta(minutes=15))

        assert result.applied is False
        assert len(tracker.list_entries()) == 1

    def test_touching_end_boundary_ignored(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        start = utcnow()
        end = start + dt.timedelta(hours=1)
        entry = TimeEntry(start=start, end=end)
        session.add(entry)
        session.commit()

        result = tracker.pause(end - dt.timedelta(minutes=15), end)

        assert result.applied is False
        assert len(tracker.list_entries()) == 1

    def test_inverted_times_raise(self, tracker: TimeTracker) -> None:
        start = utcnow()
        with pytest.raises(InvalidTimeRange):
            tracker.pause(start, start)
        with pytest.raises(InvalidTimeRange):
            tracker.pause(start, start - dt.timedelta(minutes=1))

    def test_window_spanning_two_entries_ignored(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        start = utcnow()
        entry_a = TimeEntry(start=start, end=start + dt.timedelta(hours=1))
        entry_b = TimeEntry(
            start=start + dt.timedelta(hours=1), end=start + dt.timedelta(hours=2)
        )
        session.add_all([entry_a, entry_b])
        session.commit()

        result = tracker.pause(
            start + dt.timedelta(minutes=30),
            start + dt.timedelta(hours=1, minutes=30),
        )

        assert result.applied is False
        assert len(tracker.list_entries()) == 2

    def test_open_entry_ignored(self, session: Session, tracker: TimeTracker) -> None:
        start = utcnow() - dt.timedelta(hours=1)
        entry = TimeEntry(start=start, end=None)
        session.add(entry)
        session.commit()

        result = tracker.pause(
            start + dt.timedelta(minutes=10),
            start + dt.timedelta(minutes=20),
        )

        assert result.applied is False
        assert len(tracker.list_entries()) == 1
        assert entry.end is None
