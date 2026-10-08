"""SQLAlchemy models. Every table class inherits from `Base`; Alembic reads `Base.metadata`."""

import enum
from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Integer,
    MetaData,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Deterministic constraint names, so Alembic migrations stay stable and reviewable.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class FilingStatus(enum.StrEnum):
    """Where a filing is in the ingestion pipeline (column filings.status)."""

    DISCOVERED = "discovered"
    DOWNLOADED = "downloaded"
    PARSED = "parsed"
    CHUNKED = "chunked"
    TAGGED = "tagged"
    EMBEDDED = "embedded"
    INDEXED = "indexed"
    FAILED = "failed"


_STATUS_VALUES = ", ".join(f"'{s.value}'" for s in FilingStatus)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class CompanyTicker(Base):
    """One ticker listing from SEC company_tickers.json. A company (CIK) can have several."""

    __tablename__ = "company_tickers"
    ticker: Mapped[str] = mapped_column(String(16), primary_key=True)
    cik: Mapped[int] = mapped_column(BigInteger, index=True)
    title: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(server_default=true())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Filing(Base):
    """One 10-K filing and its progress through the ingestion pipeline."""

    __tablename__ = "filings"
    __table_args__ = (CheckConstraint(f"status IN ({_STATUS_VALUES})", name="status"),)

    accession_no: Mapped[str] = mapped_column(String(20), primary_key=True)
    cik: Mapped[int] = mapped_column(BigInteger, index=True)
    form_type: Mapped[str] = mapped_column(String(10))
    filing_date: Mapped[date] = mapped_column(Date)
    report_date: Mapped[date | None] = mapped_column(Date)
    fiscal_year: Mapped[int | None] = mapped_column(Integer, index=True)
    primary_document: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(16), server_default=FilingStatus.DISCOVERED.value, index=True)
    failed_stage: Mapped[str | None] = mapped_column(String(16))
    error: Mapped[str | None] = mapped_column(Text)
    raw_object_key: Mapped[str | None] = mapped_column(Text)
    raw_sha256: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
