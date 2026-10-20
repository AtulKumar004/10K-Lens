import logging
from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy import and_, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from secrag.storage.db import session_scope
from secrag.storage.models import Filing, FilingStatus

logger = logging.getLogger(__name__)

UPDATABLE = {"status", "failed_stage", "error", "raw_object_key", "raw_sha256"}


def upsert_filing_data(session: Session, data: Sequence[dict[str, Any]]) -> int:
    """Insert new filings, skip existing accession_no. Returns how many were actually inserted.

    Runs in the caller's transaction (no commit here); use `session_scope()`.
    """
    if not data:
        raise ValueError("refusing to upsert an empty filing list")

    stmt = insert(Filing).values(list(data)).on_conflict_do_nothing(index_elements=[Filing.accession_no]).returning(Filing.accession_no)
    try:
        return len(list(session.scalars(stmt)))
    except SQLAlchemyError:
        logger.exception("DB error while inserting %d filings", len(data))
        raise


def update_filing_data(session: Session, accession_no: str, data: Mapping[str, str | int | None]) -> bool:
    """Change columns of one filing. Returns False when no filing has this accession_no.

    Only the columns in UPDATABLE can be changed (never the key, cik or dates).
    Runs in the caller's transaction (no commit here); use `session_scope()`.
    """
    if not data:
        raise ValueError("nothing to update")
    unknown = set(data) - UPDATABLE
    if unknown:
        raise ValueError(f"columns that cannot be updated: {sorted(unknown)}")

    stmt = update(Filing).where(Filing.accession_no == accession_no).values(**data).returning(Filing.accession_no)
    return session.scalar(stmt) is not None


def fetch_filing_for_download(session: Session, limit: int | None = None) -> list[dict[str, Any]]:
    """Filings that still have to be downloaded: `discovered`, or `failed` during download (to retry). Newest first."""

    data = (
        select(Filing.accession_no, Filing.cik, Filing.primary_document)
        .where(or_(Filing.status == FilingStatus.DISCOVERED, and_(Filing.status == FilingStatus.FAILED, Filing.failed_stage == "download")))
        .order_by(Filing.filing_date.desc())
        .limit(limit)
    )

    return [{"accession_no": r.accession_no, "cik": r.cik, "primary_document": r.primary_document} for r in session.execute(data)]


if __name__ == "__main__":
    with session_scope() as session:
        fetch_filing_for_download(session)
