"""Database engine and session helper."""

from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from secrag.common.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """One shared engine per process. pool_pre_ping drops dead connections."""
    return create_engine(get_settings().database_url, pool_pre_ping=True)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Commit if the block succeeds, roll back if it raises."""
    with Session(get_engine()) as session, session.begin():
        yield session
