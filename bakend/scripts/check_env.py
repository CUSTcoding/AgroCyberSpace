"""Environment and Cloud Database Diagnostic Script.

Validates that DATABASE_URL and TEST_DATABASE_URL connect successfully,
handles cloud database wake-up retries (Neon / Supabase), and checks PostGIS extension.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def normalize_db_url(url: str) -> str:
    """Ensure the URL uses the psycopg (v3) driver dialect."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def check_db_connection(
    url: str,
    db_label: str,
    retries: int = 3,
    retry_delay_seconds: float = 2.0,
) -> dict[str, Any]:
    """Test connection to a database with retry mechanism for suspended cloud instances."""
    normalized_url = normalize_db_url(url)
    result: dict[str, Any] = {
        "label": db_label,
        "success": False,
        "pg_version": None,
        "postgis_installed": False,
        "postgis_version": None,
        "error": None,
    }

    engine = create_engine(
        normalized_url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            with engine.connect() as conn:
                version_row = conn.execute(text("SELECT version();")).scalar()
                result["pg_version"] = str(version_row)

                # Check PostGIS extension
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

                if postgis_row and postgis_row["installed_version"]:
                    result["postgis_installed"] = True
                    try:
                        pgis_ver = conn.execute(text("SELECT PostGIS_Version();")).scalar()
                        result["postgis_version"] = str(pgis_ver)
                    except Exception:
                        result["postgis_version"] = str(postgis_row["installed_version"])
                elif postgis_row:
                    result["postgis_installed"] = False
                    result["postgis_version"] = (
                        f"Available ({postgis_row['default_version']}), but not enabled."
                    )
                else:
                    result["postgis_installed"] = False
                    result["postgis_version"] = "Extension not available on server"

                result["success"] = True
                return result
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(retry_delay_seconds)

    result["error"] = str(last_error)
    return result


def run_checks(env_file_path: Path | str | None = None) -> int:
    """Run all environment and connectivity checks. Returns exit code 0 or 1."""
    if env_file_path:
        load_dotenv(dotenv_path=env_file_path)
    else:
        # Load from .env if present
        load_dotenv()

    print("=" * 70)
    print("AgroSight Fair Space — Environment Diagnostic Check")
    print("=" * 70)

    # 1. Check required environment variables
    dev_db = os.getenv("DATABASE_URL")
    test_db = os.getenv("TEST_DATABASE_URL")
    direct_db = os.getenv("DATABASE_URL_DIRECT")
    jwt_secret = os.getenv("JWT_SECRET")

    missing_critical: list[str] = []
    if not dev_db:
        missing_critical.append("DATABASE_URL")
    if not test_db:
        missing_critical.append("TEST_DATABASE_URL")
    if not jwt_secret:
        missing_critical.append("JWT_SECRET")

    if missing_critical:
        print("\n❌ CRITICAL: Missing required environment variable(s):")
        for var in missing_critical:
            print(f"   - {var}")
        print("\nPlease copy .env.example to .env and configure these variables.")
        return 1

    assert dev_db is not None
    assert test_db is not None

    print("\n✅ Environment variables present:")
    print("   - DATABASE_URL: configured")
    print("   - TEST_DATABASE_URL: configured")
    print(f"   - DATABASE_URL_DIRECT: {'configured' if direct_db else 'not set (optional)'}")
    print("   - JWT_SECRET: configured")

    # 2. Check Database Connections
    databases_to_check: list[tuple[str, str]] = [
        ("Development Database", dev_db),
        ("Test Database (Isolated)", test_db),
    ]
    if direct_db:
        databases_to_check.append(("Alembic Direct Connection", direct_db))

    has_errors = False
    for label, url in databases_to_check:
        print(f"\n🔍 Testing connection to {label}...")
        status = check_db_connection(url, label)

        if status["success"]:
            print("   ✅ Connection successful!")
            if status["postgis_installed"]:
                print(f"   ✅ PostGIS extension active: {status['postgis_version']}")
            else:
                print(f"   ⚠️  PostGIS not enabled yet: {status['postgis_version']}")
                print("      (It will be enabled in migration 0.4 via CREATE EXTENSION postgis;)")
        else:
            print(f"   ❌ Connection failed: {status['error']}")
            has_errors = True

    print("\n" + "=" * 70)
    if has_errors:
        print("❌ Diagnostic finished with errors.")
        return 1

    print("✅ All database checks passed successfully!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(run_checks())
