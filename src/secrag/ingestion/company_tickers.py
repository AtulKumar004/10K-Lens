"""Fetch SEC company tickers and store them in Postgres."""

from secrag.edgar.company_tickers import fetch_company_tickers, parse_company_tickers
from secrag.storage.company_tickers import upsert_company_tickers
from secrag.storage.db import session_scope


def sync_company_tickers() -> int:
    """Download, parse and upsert in one transaction. Returns the number of rows in the file."""
    rows = parse_company_tickers(fetch_company_tickers())
    with session_scope() as session:
        upsert_company_tickers(session, rows)
    return len(rows)


if __name__ == "__main__":
    print(f"synced {sync_company_tickers()} tickers")
