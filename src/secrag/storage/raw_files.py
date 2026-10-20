import hashlib
from pathlib import Path

# Absolute, so it does not depend on the folder the script is started from.
RAW_DIR = Path(__file__).resolve().parents[3] / "data" / "raw"


def raw_key(cik: int, accession_no: str, primary_document: str) -> str:
    """Where a filing lives below RAW_DIR, always with forward slashes (this key is stored in the table)."""
    return f"{cik}/{accession_no}/{primary_document}"


def save_raw_file(cik: int, accession_no: str, primary_document: str, content: bytes) -> tuple[str, str]:
    """Write the filing bytes to RAW_DIR/<key> and return (key, sha256).

    Writes to a temporary `.part` file first and renames it, so an interrupted download never leaves a half-written file under the final name.
    """
    key = raw_key(cik, accession_no, primary_document)
    path = (RAW_DIR / key).resolve()
    if not path.is_relative_to(RAW_DIR.resolve()):
        raise ValueError(f"key escapes the raw data directory: {key!r}")
    path.parent.mkdir(parents=True, exist_ok=True)

    tmp = path.with_name(path.name + ".part")
    tmp.write_bytes(content)
    tmp.replace(path)

    return key, hashlib.sha256(content).hexdigest()


def find_raw_file(cik: int, accession_no: str, primary_document: str) -> tuple[str, str] | None:
    """If the file is already on disk (and not empty) return (key, sha256) so it need not be downloaded again."""
    key = raw_key(cik, accession_no, primary_document)
    path = RAW_DIR / key
    if not path.is_file() or path.stat().st_size == 0:
        return None
    return key, hashlib.sha256(path.read_bytes()).hexdigest()
