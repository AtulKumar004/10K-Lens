from secrag.edgar.client import sec_get

DOWNLOAD_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no}/{primary_document}"
DOWNLOAD_TIMEOUT_S = 120


def download_sec_file(cik: int, accession_no: str, primary_document: str) -> bytes:
    """
    Fetch file from https://www.sec.gov/Archives/edgar/data and return it
    """

    url = DOWNLOAD_URL.format(cik=cik, accession_no=accession_no.replace("-", ""), primary_document=primary_document)
    return sec_get(url, timeout=DOWNLOAD_TIMEOUT_S).content
