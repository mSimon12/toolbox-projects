from __future__ import annotations

import pytest

from src.core import EntryNotFound, TimeTracker


class TestDeleteEntry:
    def test_delete_entry_removes_row(self, tracker: TimeTracker) -> None:
        entry = tracker.start()
        tracker.delete(entry.id)
        assert tracker.list_entries() == []

    def test_delete_entry_raises_entry_not_found(self, tracker: TimeTracker) -> None:
        with pytest.raises(EntryNotFound):
            tracker.delete(999)
