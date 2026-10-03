def normalize_cik(cik: int | str) -> str:
    """Zero-pad a CIK to the 10-digit form EDGAR expects."""
    text = str(cik).strip()
    if not text.isdigit():
        raise ValueError(f"CIK must be numeric, got {cik!r}")
    if len(text) > 10:
        raise ValueError(f"CIK longer than 10 digits: {cik!r}")
    return text.zfill(10)
