import logging

from sqlalchemy.exc import SQLAlchemyError

from secrag.edgar.filing import fetch_10k_filings
from secrag.ingestion.corpus import CORPUS_TICKERS
from secrag.storage.company_tickers import fetch_ticker_details
from secrag.storage.db import session_scope
from secrag.storage.filling import upsert_filing_data

logger = logging.getLogger(__name__)

YEARS = {2023, 2024, 2025}


def fetch_filing_details() -> int:
    """Discover 10-K filings for every corpus ticker and store new ones. Returns total inserted."""
    total = 0
    for ticker in CORPUS_TICKERS:
        try:
            with session_scope() as session:
                row = fetch_ticker_details(session, ticker)
                cik = row.cik if row else None
            if cik is None:
                logger.warning("ticker %s not found or inactive, skipping", ticker)
                continue

            filings = fetch_10k_filings(cik, YEARS)
            if not filings:
                logger.info("no 10-K filings found for %s", ticker)
                continue

            with session_scope() as session:
                inserted = upsert_filing_data(session, filings)
            logger.info("%s: %d new filings (of %d found)", ticker, inserted, len(filings))
            total += inserted
        except SQLAlchemyError:
            logger.exception("DB error for ticker %s", ticker)
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("total inserted:", fetch_filing_details())
