"""SEC submissions API: fetch a company's filings and pick out its 10-K rows."""

import logging
from datetime import date, timedelta
from typing import Any

from secrag.edgar.client import sec_get

SUBMISSION_URL = "https://data.sec.gov/submissions/{name}"
FILING_WINDOW_DAYS = 150  # a 10-K is due 60-90 days after year end; the rest is margin for late filers

log = logging.getLogger(__name__)


def fetch_submission(cik: int) -> dict[str, Any]:
    """Fetch a company's submissions JSON. The URL needs the CIK as CIK + 10 digits + .json."""
    data = sec_get(SUBMISSION_URL.format(name=f"CIK{cik:010d}.json")).json()
    if not isinstance(data, dict):
        raise ValueError(f"expected a JSON object, got {type(data).__name__}")
    return data


def fetch_page(name: str) -> dict[str, list[Any]]:
    """Fetch one older page of a company's filings. The page itself is a block (no `filings` wrapper)."""
    data = sec_get(SUBMISSION_URL.format(name=name)).json()
    if not isinstance(data, dict):
        raise ValueError(f"expected a JSON object, got {type(data).__name__}")
    return data


def parse_10k_rows(recentBlock: dict[str, list[Any]], cik: int) -> list[dict[str, Any]]:
    """Return every 10-K in a filings recentBlock as a row for the filings table.

    A recentBlock is `submission["filings"]["recent"]` or the JSON of an older page. SEC stores each
    field as its own list, and one filing is the same position in every list.
    """

    result: list[dict[str, Any]] = []
    for i, form in enumerate(recentBlock["form"]):
        if form != "10-K":
            continue
        report = recentBlock["reportDate"][i]
        result.append(
            {
                "accession_no": recentBlock["accessionNumber"][i],
                "cik": cik,
                "form_type": form,
                "filing_date": date.fromisoformat(recentBlock["filingDate"][i]),
                "report_date": date.fromisoformat(report) if report else None,
                "fiscal_year": int(report[:4]) if report else None,
                "primary_document": recentBlock["primaryDocument"][i],
            }
        )

    return result


def pick_years(rows: list[dict[str, Any]], years: set[int]) -> tuple[list[dict[str, Any]], set[int]]:
    """Keep the rows of the wanted fiscal years, and also return the wanted years not found."""
    picked = [row for row in rows if row["fiscal_year"] in years]
    missing = years - {row["fiscal_year"] for row in picked}
    return picked, missing


def filing_window(fiscal_year_end: str | None, year: int) -> tuple[date, date] | None:
    """When the 10-K of `year` can have been filed: from the year end until FILING_WINDOW_DAYS later.

    `fiscal_year_end` is SEC's "MMDD" text, e.g. "1231". Returns None when it is missing or not a real date.
    """
    if not fiscal_year_end or len(fiscal_year_end) != 4:
        return None
    try:
        report = date(year, int(fiscal_year_end[:2]), int(fiscal_year_end[2:]))
    except ValueError:
        return None
    return report, report + timedelta(days=FILING_WINDOW_DAYS)


def candidate_pages(files: list[dict[str, Any]], window: tuple[date, date] | None) -> list[str]:
    """Names of the older pages whose filing dates overlap the window, newest first.

    Every item of `files` states its date range (filingFrom, filingTo), so no page has to be downloaded to decide.
    Without a window nothing can be ruled out, so every page is returned.
    """
    if window is None:
        return [page["name"] for page in files]
    start, end = window
    return [page["name"] for page in files if date.fromisoformat(page["filingFrom"]) <= end and date.fromisoformat(page["filingTo"]) >= start]


def fetch_10k_filings(cik: int, years: set[int]) -> list[dict[str, Any]]:
    """The 10-K rows of one company for the wanted fiscal years.

    Reads the `recent` block first. For every wanted year still missing it opens only the older pages that
    can hold that filing, newest first, and stops at the first page that has it.
    """
    submission = fetch_submission(cik)
    rows = parse_10k_rows(submission["filings"]["recent"], cik)

    found = {row["fiscal_year"] for row in rows}
    files = submission["filings"].get("files", [])

    for year in sorted(years - found, reverse=True):
        if year in found:
            continue
        window = filing_window(submission.get("fiscalYearEnd"), year)
        for name in candidate_pages(files, window):
            page_rows = parse_10k_rows(fetch_page(name), cik)
            rows += page_rows
            found |= {row["fiscal_year"] for row in page_rows}
            if year in found:
                break

    picked, missing = pick_years(rows, years)
    if missing:
        log.warning("CIK %s: no 10-K found for fiscal years %s", cik, sorted(missing))
    return list({row["accession_no"]: row for row in picked}.values())


if __name__ == "__main__":
    cik = 1045810
    data = fetch_10k_filings(cik, {2023, 2024, 2025})
    print(data)
