import pytest

from secrag.edgar.cik import normalize_cik


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(320193, "0000320193"), ("789019", "0000789019"), (" 1 ", "0000000001")],
)
def test_normalize_cik_pads(raw: int | str, expected: str) -> None:
    assert normalize_cik(raw) == expected


@pytest.mark.parametrize("bad", ["abc", "12345678901", ""])
def test_normalize_cik_rejects_invalid(bad: str) -> None:
    with pytest.raises(ValueError):
        normalize_cik(bad)
