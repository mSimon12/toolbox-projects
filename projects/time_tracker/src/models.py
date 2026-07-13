from __future__ import annotations

import datetime as dt

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    start: Mapped[dt.datetime] = mapped_column(nullable=False)
    end: Mapped[dt.datetime | None] = mapped_column(default=None)
    note: Mapped[str | None] = mapped_column(default=None)
