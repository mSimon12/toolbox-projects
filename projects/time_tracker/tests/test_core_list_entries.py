from __future__ import annotations

import datetime as dt

from sqlalchemy.orm import Session

from src.core import TimeTracker
from src.models import TimeEntry

from .conftest import utcnow


class TestListEntries:
    def test_list_entries_orders_most_recent_first(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        now = utcnow()
        session.add_all(
            [
                TimeEntry(
                    start=now - dt.timedelta(hours=2), end=now - dt.timedelta(hours=1)
                ),
                TimeEntry(start=now - dt.timedelta(hours=1), end=now),
            ]
        )
        session.commit()
        entries = tracker.list_entries()
        starts = [e.start for e in entries]
        assert starts == sorted(starts, reverse=True)

    def test_list_entries_respects_limit(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        now = utcnow()
        session.add_all(
            TimeEntry(
                start=now - dt.timedelta(hours=i + 1), end=now - dt.timedelta(hours=i)
            )
            for i in range(5)
        )
        session.commit()
        entries = tracker.list_entries(limit=2)
        assert len(entries) == 2
