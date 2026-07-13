from __future__ import annotations

import datetime as dt

import pytest
from sqlalchemy.orm import Session

from src import core
from src.models import TimeEntry


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(tzinfo=None)


class TestStartStop:
    def test_start_entry_creates_open_entry(self, session: Session) -> None:
        entry = core.start_entry(session, note="working")
        assert entry.id is not None
        assert entry.end is None
        assert entry.note == "working"

    def test_start_entry_raises_when_already_open(self, session: Session) -> None:
        core.start_entry(session)
        with pytest.raises(core.AlreadyClockedIn):
            core.start_entry(session)

    def test_stop_entry_closes_open_entry(self, session: Session) -> None:
        core.start_entry(session)
        entry = core.stop_entry(session, note="done")
        assert entry.end is not None
        assert entry.note == "done"

    def test_stop_entry_raises_when_none_open(self, session: Session) -> None:
        with pytest.raises(core.NotClockedIn):
            core.stop_entry(session)

    def test_start_allowed_again_after_stop(self, session: Session) -> None:
        core.start_entry(session)
        core.stop_entry(session)
        entry = core.start_entry(session)
        assert entry.end is None


class TestStatus:
    def test_status_when_not_clocked_in(self, session: Session) -> None:
        result = core.get_status(session)
        assert result.clocked_in is False
        assert result.entry is None
        assert result.elapsed is None

    def test_status_when_clocked_in(self, session: Session) -> None:
        core.start_entry(session)
        result = core.get_status(session)
        assert result.clocked_in is True
        assert result.entry is not None
        assert dt.timedelta(0) <= result.elapsed < dt.timedelta(seconds=5)


class TestListEntries:
    def test_list_entries_orders_most_recent_first(self, session: Session) -> None:
        now = _utcnow()
        session.add_all(
            [
                TimeEntry(
                    start=now - dt.timedelta(hours=2), end=now - dt.timedelta(hours=1)
                ),
                TimeEntry(start=now - dt.timedelta(hours=1), end=now),
            ]
        )
        session.commit()
        entries = core.list_entries(session)
        starts = [e.start for e in entries]
        assert starts == sorted(starts, reverse=True)

    def test_list_entries_respects_limit(self, session: Session) -> None:
        now = _utcnow()
        session.add_all(
            TimeEntry(
                start=now - dt.timedelta(hours=i + 1), end=now - dt.timedelta(hours=i)
            )
            for i in range(5)
        )
        session.commit()
        entries = core.list_entries(session, limit=2)
        assert len(entries) == 2


class TestReport:
    def test_today_period_includes_entry_started_now(self, session: Session) -> None:
        core.start_entry(session)
        core.stop_entry(session)
        result = core.report(session, core.today_period())
        assert len(result.entries) == 1
        assert result.total > dt.timedelta(0)

    def test_today_period_excludes_entry_from_two_days_ago(
        self, session: Session
    ) -> None:
        old_start = _utcnow() - dt.timedelta(days=2)
        session.add(TimeEntry(start=old_start, end=old_start + dt.timedelta(hours=1)))
        session.commit()
        result = core.report(session, core.today_period())
        assert result.entries == []
        assert result.total == dt.timedelta(0)

    def test_report_counts_open_entry_up_to_now(self, session: Session) -> None:
        core.start_entry(session)
        result = core.report(session, core.today_period())
        assert len(result.entries) == 1
        assert result.total > dt.timedelta(0)

    def test_week_period_includes_entry_started_now(self, session: Session) -> None:
        core.start_entry(session)
        core.stop_entry(session)
        result = core.report(session, core.week_period())
        assert len(result.entries) == 1

    def test_week_period_excludes_entry_from_thirty_days_ago(
        self, session: Session
    ) -> None:
        old_start = _utcnow() - dt.timedelta(days=30)
        session.add(TimeEntry(start=old_start, end=old_start + dt.timedelta(hours=1)))
        session.commit()
        result = core.report(session, core.week_period())
        assert result.entries == []

    def test_custom_period_includes_entry_within_range(self, session: Session) -> None:
        core.start_entry(session)
        core.stop_entry(session)
        yesterday = dt.date.today() - dt.timedelta(days=1)
        today = dt.date.today()
        result = core.report(session, core.custom_period(yesterday, today))
        assert len(result.entries) == 1

    def test_custom_period_excludes_entry_outside_range(self, session: Session) -> None:
        old_start = _utcnow() - dt.timedelta(days=10)
        session.add(TimeEntry(start=old_start, end=old_start + dt.timedelta(hours=1)))
        session.commit()
        yesterday = dt.date.today() - dt.timedelta(days=1)
        today = dt.date.today()
        result = core.report(session, core.custom_period(yesterday, today))
        assert result.entries == []
