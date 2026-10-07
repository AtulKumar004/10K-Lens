"""Download SEC's company_tickers.json (ticker -> CIK -> company name)."""

from typing import Any

import requests

from secrag.common.config import get_settings

TICKER_URL = "https://www.sec.gov/files/company_tickers.json"


def fetch_company_tickers(timeout: float = 30.0) -> dict[str, Any]:
    """Fetch the raw JSON. Raises requests.RequestException
    on network errors or non-2xx responses."""
    headers = {"User-Agent": get_settings().sec_user_agent}
    responses = requests.get(TICKER_URL, headers=headers, timeout=timeout)
    responses.raise_for_status()
    data = responses.json()
    if not isinstance(data, dict):
        raise ValueError(f"expected a JSON object, got {type(data).__name__}")
    return data


def parse_company_tickers(raw: dict[str, Any]) -> list[dict[str, Any]]:
    """Turn SEC's {"0": {...}, "1": {...}} into a flat list of rows for the table."""
    return [
        {"ticker": item["ticker"], "cik": int(item["cik_str"]), "title": item["title"]}
        for item in raw.values()
    ]


if __name__ == "__main__":
    data = fetch_company_tickers()
    for i in range(10):
        print(data[str(i)])
