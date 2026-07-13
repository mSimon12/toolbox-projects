from __future__ import annotations

import datetime as dt

from sqlalchemy.orm import Session

from src.core import ReportPeriod, TimeTracker
from src.models import TimeEntry

from .conftest import utcnow


class TestReport:
    def test_today_period_includes_entry_started_now(
        self, tracker: TimeTracker
    ) -> None:
        tracker.start()
        tracker.stop()
        result = tracker.report(ReportPeriod.today())
        assert len(result.entries) == 1
        assert result.total > dt.timedelta(0)

    def test_today_period_excludes_entry_from_two_days_ago(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        old_start = utcnow() - dt.timedelta(days=2)
        session.add(TimeEntry(start=old_start, end=old_start + dt.timedelta(hours=1)))
        session.commit()
        result = tracker.report(ReportPeriod.today())
        assert result.entries == []
        assert result.total == dt.timedelta(0)

    def test_report_counts_open_entry_up_to_now(self, tracker: TimeTracker) -> None:
        tracker.start()
        result = tracker.report(ReportPeriod.today())
        assert len(result.entries) == 1
        assert result.total > dt.timedelta(0)

    def test_week_period_includes_entry_started_now(self, tracker: TimeTracker) -> None:
        tracker.start()
        tracker.stop()
        result = tracker.report(ReportPeriod.this_week())
        assert len(result.entries) == 1

    def test_week_period_excludes_entry_from_thirty_days_ago(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        old_start = utcnow() - dt.timedelta(days=30)
        session.add(TimeEntry(start=old_start, end=old_start + dt.timedelta(hours=1)))
        session.commit()
        result = tracker.report(ReportPeriod.this_week())
        assert result.entries == []

    def test_custom_period_includes_entry_within_range(
        self, tracker: TimeTracker
    ) -> None:
        tracker.start()
        tracker.stop()
        yesterday = dt.date.today() - dt.timedelta(days=1)
        today = dt.date.today()
        result = tracker.report(ReportPeriod.custom(yesterday, today))
        assert len(result.entries) == 1

    def test_custom_period_excludes_entry_outside_range(
        self, session: Session, tracker: TimeTracker
    ) -> None:
        old_start = utcnow() - dt.timedelta(days=10)
        session.add(TimeEntry(start=old_start, end=old_start + dt.timedelta(hours=1)))
        session.commit()
        yesterday = dt.date.today() - dt.timedelta(days=1)
        today = dt.date.today()
        result = tracker.report(ReportPeriod.custom(yesterday, today))
        assert result.entries == []
