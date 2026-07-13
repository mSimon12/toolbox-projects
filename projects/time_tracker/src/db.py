from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.models import Base

DEFAULT_DB_PATH = Path.home() / ".time_tracker" / "time_tracker.db"

SessionLocal: sessionmaker[Session] = sessionmaker()


def get_db_path() -> Path:
    env_path = os.environ.get("TIME_TRACKER_DB")
    return Path(env_path) if env_path else DEFAULT_DB_PATH


def get_engine(db_path: Path | None = None) -> Engine:
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{path}")


def init_db(engine: Engine | None = None) -> Engine:
    engine = engine or get_engine()
    Base.metadata.create_all(engine)
    SessionLocal.configure(bind=engine)
    return engine
