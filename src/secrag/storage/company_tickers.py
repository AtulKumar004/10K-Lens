from collections.abc import Sequence
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from secrag.storage.models import CompanyTicker


def upsert_company_tickers(session: Session, data: Sequence[dict[str, Any]]) -> None:
    """Insert new tickers, update existing ones, and mark tickers missing from `data` inactive.

    Runs inside the caller's transaction: no commit here. Use `session_scope()` so that
    either both statements are saved or neither is.
    """
    if not data:
        # Empty input would mark EVERY ticker inactive. Treat it as a bad fetch, not a real result.
        raise ValueError("refusing to upsert an empty ticker list")

    stmt = insert(CompanyTicker)
    stmt = stmt.on_conflict_do_update(
        index_elements=[CompanyTicker.ticker],
        set_={"cik": stmt.excluded.cik, "title": stmt.excluded.title, "is_active": True},
    )
    session.execute(stmt, data)

    seen = [row["ticker"] for row in data]
    session.execute(update(CompanyTicker).where(CompanyTicker.is_active.is_(True), CompanyTicker.ticker.not_in(seen)).values(is_active=False))


def fetch_ticker_details(session: Session, ticker: str) -> CompanyTicker | None:
    """Return the active row for `ticker`, or None if unknown/inactive."""
    data = select(CompanyTicker).where(
        CompanyTicker.ticker == ticker.upper(),
        CompanyTicker.is_active.is_(True),
    )
    return session.execute(data).scalar_one_or_none()


if __name__ == "__main__":
    from secrag.storage.db import session_scope

    with session_scope() as session:
        row = fetch_ticker_details(session, "AAPL")
        print(row.cik, row.title) if row else print("not found")
