import json
from pathlib import Path
from typing import Any

import pytest

from secrag.edgar.company_tickers import parse_company_tickers

FIXTURE = Path(__file__).parent / "fixtures" / "company_tickers_sample.json"


@pytest.fixture
def raw() -> dict[str, Any]:
    """A saved slice of SEC's real company_tickers.json."""
    data: dict[str, Any] = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return data


def test_parse_flattens_sec_object_into_rows(raw: dict[str, Any]) -> None:
    rows = parse_company_tickers(raw)

    assert len(rows) == 6
    assert rows[0] == {"ticker": "NVDA", "cik": 1045810, "title": "NVIDIA CORP"}


def test_parse_keeps_one_row_per_ticker_when_a_company_has_several(raw: dict[str, Any]) -> None:
    rows = parse_company_tickers(raw)

    alphabet = [row["ticker"] for row in rows if row["cik"] == 1652044]
    assert alphabet == ["GOOGL", "GOOG"]
    assert len({row["ticker"] for row in rows}) == len(rows)


def test_parse_returns_only_the_table_columns(raw: dict[str, Any]) -> None:
    for row in parse_company_tickers(raw):
        assert set(row) == {"ticker", "cik", "title"}


@pytest.mark.parametrize("cik_value", [320193, "320193"])
def test_parse_returns_cik_as_int(cik_value: int | str) -> None:
    raw = {"0": {"cik_str": cik_value, "ticker": "AAPL", "title": "Apple Inc."}}

    (row,) = parse_company_tickers(raw)

    assert row["cik"] == 320193
    assert isinstance(row["cik"], int)


def test_parse_empty_object_gives_no_rows() -> None:
    assert parse_company_tickers({}) == []


@pytest.mark.parametrize("missing", ["cik_str", "ticker", "title"])
def test_parse_raises_when_a_field_is_missing(missing: str) -> None:
    item = {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
    del item[missing]

    with pytest.raises(KeyError):
        parse_company_tickers({"0": item})


def test_parse_raises_on_non_numeric_cik() -> None:
    raw = {"0": {"cik_str": "abc", "ticker": "AAPL", "title": "Apple Inc."}}

    with pytest.raises(ValueError):
        parse_company_tickers(raw)
