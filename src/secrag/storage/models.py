"""SQLAlchemy models. Every table class inherits from `Base`; Alembic reads `Base.metadata`."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, MetaData, String, func, true
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Deterministic constraint names, so Alembic migrations stay stable and reviewable.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class CompanyTicker(Base):
    """One ticker listing from SEC company_tickers.json. A company (CIK) can have several."""

    __tablename__ = "company_tickers"
    ticker: Mapped[str] = mapped_column(String(16), primary_key=True)
    cik: Mapped[int] = mapped_column(BigInteger, index=True)
    title: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(server_default=true())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
