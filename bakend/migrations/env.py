from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import app.modules.agriculture.models  # noqa: F401
import app.modules.regions.models  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.core.config import settings
from app.core.database import Base
from scripts.check_env import normalize_db_url

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = getattr(context, "config", None)

# Interpret the config file for Python logging.
if config is not None and config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def get_migration_url() -> str:
    """Determine the database URL for migrations.

    Prefers DATABASE_URL_DIRECT (bypassing connection poolers for DDL safety),
    falling back to DATABASE_URL.
    """
    url = settings.DATABASE_URL_DIRECT or settings.DATABASE_URL
    if not url and config is not None:
        # Fall back to alembic.ini configured url or placeholder
        url = config.get_main_option(
            "sqlalchemy.url", "postgresql+psycopg://postgres:postgres@localhost/agrosight"
        )
    return normalize_db_url(url or "postgresql+psycopg://postgres:postgres@localhost/agrosight")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_migration_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section, {}) if config is not None else {}
    configuration["sqlalchemy.url"] = get_migration_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if config is not None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
