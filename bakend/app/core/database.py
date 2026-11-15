"""Database connection, engine configuration, session lifecycle, and cloud health check."""

from __future__ import annotations

import time
from collections.abc import Generator
from typing import Any

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


_engine: Engine | None = None


def get_engine(db_url: str | None = None) -> Engine:
    """Return existing engine or create a new one with connection pooling and timeouts."""
    global _engine
    target_url = db_url or settings.sync_database_url

    if not target_url:
        raise ValueError("DATABASE_URL is not configured.")

    if _engine is None or db_url is not None:
        new_engine = create_engine(
            target_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10},
        )
        if db_url is None:
            _engine = new_engine
        return new_engine

    return _engine


def get_session_factory(db_engine: Engine | None = None) -> sessionmaker[Session]:
    """Get configured sessionmaker."""
    eng = db_engine or get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=eng)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database sessions."""
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def check_db_health(
    retries: int = 3,
    retry_delay_seconds: float = 1.0,
    db_engine: Engine | None = None,
) -> dict[str, Any]:
    """Perform a health check on the database with retries for cloud wake-up.

    Returns a dictionary detailing connectivity, latency, and PostGIS availability.
    """
    if not settings.DATABASE_URL and db_engine is None:
        return {
            "status": "not_configured",
            "latency_ms": None,
            "postgis_installed": False,
            "postgis_version": None,
            "error": "DATABASE_URL is not set",
        }

    try:
        eng = db_engine or get_engine()
    except Exception as exc:
        return {
            "status": "error",
            "latency_ms": None,
            "postgis_installed": False,
            "postgis_version": None,
            "error": str(exc),
        }

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            start_time = time.perf_counter()
            with eng.connect() as conn:
                # 1. Test basic connectivity
                conn.execute(text("SELECT 1;"))
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

                # 2. Check PostGIS extension status
                postgis_row = (
                    conn.execute(
                        text(
                            "SELECT default_version, installed_version "
                            "FROM pg_available_extensions WHERE name = 'postgis';"
                        )
                    )
                    .mappings()
                    .first()
                )

                postgis_installed = False
                postgis_version: str | None = None

                if postgis_row and postgis_row["installed_version"]:
                    postgis_installed = True
                    try:
                        pgis_ver = conn.execute(text("SELECT PostGIS_Version();")).scalar()
                        postgis_version = str(pgis_ver)
                    except Exception:
                        postgis_version = str(postgis_row["installed_version"])
                elif postgis_row:
                    postgis_version = (
                        f"Available ({postgis_row['default_version']}), not yet enabled."
                    )
                else:
                    postgis_version = "Not available on host"

                return {
                    "status": "ok",
                    "latency_ms": latency_ms,
                    "postgis_installed": postgis_installed,
                    "postgis_version": postgis_version,
                    "error": None,
                }
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(retry_delay_seconds)

    return {
        "status": "error",
        "latency_ms": None,
        "postgis_installed": False,
        "postgis_version": None,
        "error": str(last_error),
    }
