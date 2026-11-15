"""Unit tests for the environment and database diagnostic script."""

from unittest.mock import MagicMock, patch

from scripts.check_env import check_db_connection, normalize_db_url, run_checks


def test_normalize_db_url() -> None:
    assert (
        normalize_db_url("postgres://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"
    )
    assert (
        normalize_db_url("postgresql://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )
    assert (
        normalize_db_url("postgresql+psycopg://user:pass@host/db")
        == "postgresql+psycopg://user:pass@host/db"
    )


@patch("scripts.check_env.create_engine")
def test_check_db_connection_success(mock_create_engine: MagicMock) -> None:
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # First execute: SELECT version()
    # Second execute: SELECT default_version, installed_version ...
    # Third execute: SELECT PostGIS_Version()
    mock_version = MagicMock()
    mock_version.scalar.return_value = "PostgreSQL 16.1 on x86_64"

    mock_postgis_row = {"default_version": "3.4.0", "installed_version": "3.4.0"}
    mock_postgis_query = MagicMock()
    mock_postgis_query.mappings.return_value.first.return_value = mock_postgis_row

    mock_pgis_ver = MagicMock()
    mock_pgis_ver.scalar.return_value = "3.4.0 USE_GEOS=1"

    mock_conn.execute.side_effect = [mock_version, mock_postgis_query, mock_pgis_ver]

    result = check_db_connection("postgresql+psycopg://localhost/test", "Test DB", retries=1)

    assert result["success"] is True
    assert result["pg_version"] == "PostgreSQL 16.1 on x86_64"
    assert result["postgis_installed"] is True
    assert "3.4.0" in str(result["postgis_version"])


@patch("scripts.check_env.create_engine")
def test_check_db_connection_failure_retries(mock_create_engine: MagicMock) -> None:
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.side_effect = ConnectionError("Could not reach cloud host")

    result = check_db_connection(
        "postgresql+psycopg://localhost/test", "Test DB", retries=2, retry_delay_seconds=0.01
    )

    assert result["success"] is False
    assert "Could not reach cloud host" in str(result["error"])
    assert mock_engine.connect.call_count == 2


def test_run_checks_missing_vars() -> None:
    with patch.dict("os.environ", {}, clear=True):
        exit_code = run_checks()
        assert exit_code == 1


@patch("scripts.check_env.check_db_connection")
def test_run_checks_success(mock_check_db: MagicMock) -> None:
    mock_check_db.return_value = {
        "label": "Test",
        "success": True,
        "pg_version": "PostgreSQL 16",
        "postgis_installed": True,
        "postgis_version": "3.4.0",
        "error": None,
    }
    fake_env = {
        "DATABASE_URL": "postgresql+psycopg://user:pass@host/dev_db",
        "TEST_DATABASE_URL": "postgresql+psycopg://user:pass@host/test_db",
        "JWT_SECRET": "a" * 32,
    }
    with patch.dict("os.environ", fake_env, clear=True):
        exit_code = run_checks()
        assert exit_code == 0
        assert mock_check_db.call_count == 2
