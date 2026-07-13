from __future__ import annotations

import datetime as dt

from src.core import TimeTracker


class TestStatus:
    def test_status_when_not_clocked_in(self, tracker: TimeTracker) -> None:
        result = tracker.status()
        assert result.clocked_in is False
        assert result.entry is None
        assert result.elapsed is None

    def test_status_when_clocked_in(self, tracker: TimeTracker) -> None:
        tracker.start()
        result = tracker.status()
        assert result.clocked_in is True
        assert result.entry is not None
        assert dt.timedelta(0) <= result.elapsed < dt.timedelta(seconds=5)
