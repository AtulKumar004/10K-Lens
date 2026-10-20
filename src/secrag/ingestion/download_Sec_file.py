import logging
import sys

import requests

from secrag.edgar.download_sec import download_sec_file
from secrag.storage.db import session_scope
from secrag.storage.filling import fetch_filing_for_download, update_filing_data
from secrag.storage.models import FilingStatus
from secrag.storage.raw_files import find_raw_file, save_raw_file

log = logging.getLogger(__name__)


def download_sec_files(limit: int | None = None) -> dict[str, int]:
    """Download every filing that is still waiting (or failed earlier), save it under data/raw and record the result in the table.

    A file that is already on disk is only registered, not downloaded again. One failing filing does not stop the others.
    """
    with session_scope() as session:  # the session is closed before any download starts
        filings = fetch_filing_for_download(session, limit)

    downloaded = failed = 0
    for filing in filings:
        accession_no, cik, document = filing["accession_no"], filing["cik"], filing["primary_document"]
        try:
            found = find_raw_file(cik, accession_no, document)
            if found is None:
                found = save_raw_file(cik, accession_no, document, download_sec_file(cik, accession_no, document))
        except (requests.RequestException, OSError) as exc:
            log.error("download failed for %s: %s", accession_no, exc)
            with session_scope() as session:
                update_filing_data(session, accession_no, {"status": FilingStatus.FAILED, "failed_stage": "download", "error": str(exc)[:2000]})
            failed += 1
            continue

        key, sha256 = found
        with session_scope() as session:
            update_filing_data(
                session,
                accession_no,
                {"status": FilingStatus.DOWNLOADED, "raw_object_key": key, "raw_sha256": sha256, "failed_stage": None, "error": None},
            )
        downloaded += 1
    return {"downloaded": downloaded, "failed": failed}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print(download_sec_files(int(sys.argv[1]) if len(sys.argv) > 1 else None))
