"""Integration tests for Regions, Districts, and Communities endpoints."""

import uuid
from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.modules.regions.models import Community, District, Region


@pytest.fixture
def mock_region_db() -> tuple[MagicMock, Region, District, Community]:
    """Create mock database with interconnected Region, District, and Community."""
    mock_db = MagicMock()
    region_id = uuid.uuid4()
    district_id = uuid.uuid4()
    community_id = uuid.uuid4()

    region = Region(
        id=region_id,
        code="gaza",
        name="Gaza",
        description="Chókwè e vale do Limpopo",
        is_proposed_study_area=True,
    )
    district = District(
        id=district_id,
        region_id=region_id,
        code="chokwe",
        name="Chókwè",
        province="Gaza",
        source="CENACARTA 2017",
    )
    community = Community(
        id=community_id,
        district_id=district_id,
        name="Lionde",
        description="Zona de regadio",
    )

    return mock_db, region, district, community


@pytest.mark.anyio
async def test_list_regions(mock_region_db: tuple[MagicMock, Region, District, Community]) -> None:
    """Test GET /api/v1/regions with pagination."""
    mock_db, region, _, _ = mock_region_db

    # Setup mock behavior
    mock_db.scalars.return_value.all.return_value = [region]
    mock_db.execute.return_value.scalar.return_value = 1

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/regions?limit=10&offset=0")
            assert resp.status_code == 200
            data = resp.json()
            assert "items" in data
            assert data["total"] == 1
            assert data["limit"] == 10
            assert data["offset"] == 0
            assert len(data["items"]) == 1
            assert data["items"][0]["code"] == "gaza"
            assert data["items"][0]["name"] == "Gaza"
            assert data["items"][0]["is_proposed_study_area"] is True
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
async def test_get_region_found(
    mock_region_db: tuple[MagicMock, Region, District, Community],
) -> None:
    """Test GET /api/v1/regions/{id} when found."""
    mock_db, region, _, _ = mock_region_db
    mock_db.scalars.return_value.first.return_value = region

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/regions/{region.id}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["id"] == str(region.id)
            assert data["code"] == "gaza"
            assert data["name"] == "Gaza"
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
async def test_get_region_not_found(
    mock_region_db: tuple[MagicMock, Region, District, Community],
) -> None:
    """Test GET /api/v1/regions/{id} when not found returns 404 with error envelope."""
    mock_db, _, _, _ = mock_region_db
    mock_db.scalars.return_value.first.return_value = None

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            fake_id = uuid.uuid4()
            resp = await client.get(f"/api/v1/regions/{fake_id}")
            assert resp.status_code == 404
            data = resp.json()
            assert "error" in data
            assert data["error"]["code"] == "NOT_FOUND"
            assert str(fake_id) in data["error"]["message"]
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
async def test_list_districts_in_region(
    mock_region_db: tuple[MagicMock, Region, District, Community],
) -> None:
    """Test GET /api/v1/regions/{id}/districts."""
    mock_db, region, district, _ = mock_region_db
    mock_db.scalars.return_value.first.return_value = region
    mock_db.scalars.return_value.all.return_value = [district]
    mock_db.execute.return_value.scalar.return_value = 1

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/regions/{region.id}/districts")
            assert resp.status_code == 200
            data = resp.json()
            assert "items" in data
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["code"] == "chokwe"
            assert data["items"][0]["name"] == "Chókwè"
            assert data["items"][0]["source"] == "CENACARTA 2017"
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
async def test_list_communities_in_region(
    mock_region_db: tuple[MagicMock, Region, District, Community],
) -> None:
    """Test GET /api/v1/regions/{id}/communities."""
    mock_db, region, _, community = mock_region_db
    mock_db.scalars.return_value.first.return_value = region
    mock_db.scalars.return_value.all.return_value = [community]
    mock_db.execute.return_value.scalar.return_value = 1

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/regions/{region.id}/communities")
            assert resp.status_code == 200
            data = resp.json()
            assert "items" in data
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["name"] == "Lionde"
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
async def test_get_region_map_geojson(
    mock_region_db: tuple[MagicMock, Region, District, Community],
) -> None:
    """Test GET /api/v1/regions/{id}/map returns GeoJSON Feature."""
    mock_db, region, _, _ = mock_region_db
    mock_db.scalars.return_value.first.return_value = region

    mock_row: Any = MagicMock()
    mock_row.id = region.id
    mock_row.code = region.code
    mock_row.name = region.name
    mock_row.description = region.description
    mock_row.is_proposed_study_area = True
    mock_row.geojson = (
        '{"type": "Polygon", "coordinates": [[[32.85, -24.3], [33.25, -24.3], '
        "[33.35, -24.6], [32.85, -24.3]]]}"
    )
    mock_db.execute.return_value.first.return_value = mock_row

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/regions/{region.id}/map")
            assert resp.status_code == 200
            data = resp.json()
            assert data["type"] == "Feature"
            assert data["id"] == str(region.id)
            assert data["properties"]["code"] == "gaza"
            assert data["geometry"]["type"] == "Polygon"
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
async def test_invalid_uuid_returns_422() -> None:
    """Test endpoint with invalid UUID returns 422 with validation error format."""
    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/regions/not-a-valid-uuid")
            assert resp.status_code == 422
            data = resp.json()
            assert "error" in data
            assert data["error"]["code"] == "VALIDATION_ERROR"
    finally:
        app.dependency_overrides.pop(get_db, None)
