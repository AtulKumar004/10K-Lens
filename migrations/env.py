"""Alembic environment: DB URL from .env (via Settings), schema from secrag.storage.models."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from secrag.common.config import get_settings
from secrag.storage.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL to stdout (`alembic upgrade head --sql`). Needs only the dialect, no credentials."""
    context.configure(
        dialect_name="postgresql",
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Connect to the database from .env and apply migrations."""
    engine = create_engine(get_settings().database_url, poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
