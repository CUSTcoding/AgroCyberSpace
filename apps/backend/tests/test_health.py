"""Unit and integration tests for the /health endpoint and database health checks."""

from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.database import check_db_health, get_db, get_engine
from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.mark.asyncio
async def test_health_not_configured() -> None:
    transport = ASGITransport(app=app)
    with patch("app.main.check_db_health") as mock_health:
        mock_health.return_value = {
            "status": "not_configured",
            "latency_ms": None,
            "postgis_installed": False,
            "postgis_version": None,
            "error": "DATABASE_URL is not set",
        }
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["api"] == "ok"
        assert data["database"]["status"] == "not_configured"


@pytest.mark.asyncio
async def test_health_healthy_with_postgis() -> None:
    transport = ASGITransport(app=app)
    with patch("app.main.check_db_health") as mock_health:
        mock_health.return_value = {
            "status": "ok",
            "latency_ms": 14.2,
            "postgis_installed": True,
            "postgis_version": "3.4.0 USE_GEOS=1",
            "error": None,
        }
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["api"] == "ok"
        assert data["database"]["status"] == "ok"
        assert data["database"]["latency_ms"] == 14.2
        assert data["postgis"]["installed"] is True
        assert data["postgis"]["version"] == "3.4.0 USE_GEOS=1"


@pytest.mark.asyncio
async def test_health_database_error_returns_503() -> None:
    transport = ASGITransport(app=app)
    with patch("app.main.check_db_health") as mock_health:
        mock_health.return_value = {
            "status": "error",
            "latency_ms": None,
            "postgis_installed": False,
            "postgis_version": None,
            "error": "Connection timed out",
        }
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database"]["status"] == "error"
        assert data["database"]["error"] == "Connection timed out"


@pytest.mark.asyncio
async def test_health_api_v1_prefix() -> None:
    transport = ASGITransport(app=app)
    with patch("app.main.check_db_health") as mock_health:
        mock_health.return_value = {
            "status": "ok",
            "latency_ms": 5.0,
            "postgis_installed": True,
            "postgis_version": "3.4",
            "error": None,
        }
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_cors_origins_parsing() -> None:
    # Comma-separated
    s1 = Settings(CORS_ORIGINS="http://localhost:3000,http://app.local")  # type: ignore[arg-type]
    assert s1.CORS_ORIGINS == ["http://localhost:3000", "http://app.local"]

    # JSON list string
    s2 = Settings(CORS_ORIGINS='["http://localhost:3000"]')  # type: ignore[arg-type]
    assert s2.CORS_ORIGINS == ["http://localhost:3000"]


def test_database_get_engine_error_when_empty() -> None:
    with pytest.raises(ValueError, match="DATABASE_URL is not configured"):
        get_engine("")


def test_check_db_health_with_mocked_engine() -> None:
    mock_engine = MagicMock()
    mock_conn = MagicMock()
    mock_engine.connect.return_value.__enter__.return_value = mock_conn

    # 1. SELECT 1;
    # 2. SELECT default_version, installed_version ...
    # 3. SELECT PostGIS_Version();
    mock_postgis_row = {"default_version": "3.4.0", "installed_version": "3.4.0"}
    mock_postgis_query = MagicMock()
    mock_postgis_query.mappings.return_value.first.return_value = mock_postgis_row
    mock_pgis_ver = MagicMock()
    mock_pgis_ver.scalar.return_value = "3.4.0"

    mock_conn.execute.side_effect = [MagicMock(), mock_postgis_query, mock_pgis_ver]

    result: dict[str, Any] = check_db_health(retries=1, db_engine=mock_engine)
    assert result["status"] == "ok"
    assert result["postgis_installed"] is True
    assert result["postgis_version"] == "3.4.0"


def test_get_db_yields_session() -> None:
    mock_session = MagicMock()
    with patch("app.core.database.get_session_factory") as mock_factory:
        mock_factory.return_value = MagicMock(return_value=mock_session)
        gen: Generator[Any, None, None] = get_db()
        session = next(gen)
        assert session == mock_session
        with pytest.raises(StopIteration):
            next(gen)
        mock_session.close.assert_called_once()
