from __future__ import annotations

import datetime as dt
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from src.core import TimeTracker
from src.models import Base


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.UTC).replace(tzinfo=None)


@pytest.fixture
def session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with Session(engine) as sess:
        yield sess
    engine.dispose()


@pytest.fixture
def tracker(session: Session) -> TimeTracker:
    return TimeTracker(session)
