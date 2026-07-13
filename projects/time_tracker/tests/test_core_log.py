from __future__ import annotations

import datetime as dt

import pytest

from src.core import EntryExistsForDay, InvalidTimeRange, TimeTracker


class TestLogEntry:
    def test_log_entry_creates_correct_duration(self, tracker: TimeTracker) -> None:
        entry = tracker.log(
            dt.date.today(), dt.time(9, 0), dt.time(12, 30), note="past work"
        )
        assert entry.end - entry.start == dt.timedelta(hours=3.5)
        assert entry.note == "past work"

    def test_log_entry_uses_given_start_and_end(self, tracker: TimeTracker) -> None:
        day = dt.date.today()
        entry = tracker.log(day, dt.time(10, 0), dt.time(11, 0))
        local_start = entry.start.replace(tzinfo=dt.UTC).astimezone()
        local_end = entry.end.replace(tzinfo=dt.UTC).astimezone()
        assert local_start.hour == 10
        assert local_start.date() == day
        assert local_end.hour == 11

    def test_log_entry_rejects_end_before_start(self, tracker: TimeTracker) -> None:
        day = dt.date.today()
        with pytest.raises(InvalidTimeRange):
            tracker.log(day, dt.time(9, 0), dt.time(8, 0))

    def test_log_entry_rejects_duplicate_day(self, tracker: TimeTracker) -> None:
        day = dt.date.today()
        tracker.log(day, dt.time(9, 0), dt.time(10, 0))
        with pytest.raises(EntryExistsForDay):
            tracker.log(day, dt.time(11, 0), dt.time(13, 0))

    def test_log_entry_force_overrides_duplicate_day(
        self, tracker: TimeTracker
    ) -> None:
        day = dt.date.today()
        tracker.log(day, dt.time(9, 0), dt.time(10, 0))
        tracker.log(day, dt.time(11, 0), dt.time(13, 0), force=True)
        entries = tracker.list_entries()
        assert len(entries) == 2
