"""Shared HTTP access to SEC EDGAR: declared User-Agent, rate limit, timeout and retries.

Every request to sec.gov / data.sec.gov goes through `sec_get`. The limiter is per process;
when several workers run it moves to a shared Redis token bucket (see docs/architecture.pdf).
"""

import threading
import time

import requests

from secrag.common.config import get_settings

MIN_INTERVAL_S = 0.125  # 8 requests/second, under SEC's 10/second cap
MAX_ATTEMPTS = 3
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})

_lock = threading.Lock()
_last_request = 0.0


def _wait_for_slot() -> None:
    """Block until MIN_INTERVAL_S has passed since the previous request."""
    global _last_request
    with _lock:
        delay = _last_request + MIN_INTERVAL_S - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        _last_request = time.monotonic()


def sec_get(url: str, timeout: float = 30.0) -> requests.Response:
    """GET a SEC URL. Retries connection errors, timeouts, 429 and 5xx with backoff (2s, 4s).

    Raises requests.RequestException once attempts are used up, or at once on other 4xx errors.
    """
    headers = {"User-Agent": get_settings().sec_user_agent}
    for attempt in range(1, MAX_ATTEMPTS + 1):
        _wait_for_slot()
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout):
            if attempt == MAX_ATTEMPTS:
                raise
        else:
            if response.status_code not in RETRY_STATUSES or attempt == MAX_ATTEMPTS:
                response.raise_for_status()
                return response
        time.sleep(2**attempt)
    raise AssertionError("unreachable")
