import logging
from collections.abc import Sequence
from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from secrag.storage.models import Filing

logger = logging.getLogger(__name__)


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
