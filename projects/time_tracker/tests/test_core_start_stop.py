from __future__ import annotations

import pytest

from src.core import AlreadyClockedIn, NotClockedIn, TimeTracker


class TestStartStop:
    def test_start_entry_creates_open_entry(self, tracker: TimeTracker) -> None:
        entry = tracker.start(note="working")
        assert entry.id is not None
        assert entry.end is None
        assert entry.note == "working"

    def test_start_entry_raises_when_already_open(self, tracker: TimeTracker) -> None:
        tracker.start()
        with pytest.raises(AlreadyClockedIn):
            tracker.start()

    def test_stop_entry_closes_open_entry(self, tracker: TimeTracker) -> None:
        tracker.start()
        entry = tracker.stop(note="done")
        assert entry.end is not None
        assert entry.note == "done"

    def test_stop_entry_raises_when_none_open(self, tracker: TimeTracker) -> None:
        with pytest.raises(NotClockedIn):
            tracker.stop()

    def test_start_allowed_again_after_stop(self, tracker: TimeTracker) -> None:
        tracker.start()
        tracker.stop()
        entry = tracker.start()
        assert entry.end is None
