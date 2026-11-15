"""Tests for persisted NASA POWER ingestion orchestration."""

import uuid
from datetime import date
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.modules.earth_observation.models import Dataset, IngestionRun
from app.modules.earth_observation.router import get_earth_observation_service
from app.modules.earth_observation.service import EarthObservationService


def power_payload() -> dict[str, object]:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [32.5, -24.5, 0]},
                "properties": {"parameter": {"T2M": {"20260101": 27.1, "20260102": -999}}},
            }
        ],
        "parameters": {"T2M": {"units": "C", "longname": "Temperature at 2 Meters"}},
        "header": {"fill_value": -999, "api": {"version": "v2.10.3"}},
        "messages": [],
    }


def test_ingest_power_persists_point_values_and_provenance() -> None:
    db = MagicMock()
    client = MagicMock()
    client.fetch_daily_regional.return_value = power_payload()
    client.parse_regional_response.return_value = (
        "C",
        [
            {
                "observed_at": date(2026, 1, 1),
                "latitude": -24.5,
                "longitude": 32.5,
                "value": 27.1,
            }
        ],
    )
    service = EarthObservationService(db, client=client)
    run = IngestionRun(
        region_id=uuid.uuid4(),
        source="NASA POWER",
        product="POWER Daily Regional",
        time_start=date(2026, 1, 1),
        time_end=date(2026, 1, 2),
        status="running",
    )
    service.repo = MagicMock()
    service.repo.create_run.return_value = run
    service.repo.get_region_boundary.return_value = {
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [32.0, -25.0],
                [33.0, -25.0],
                [33.0, -24.0],
                [32.0, -24.0],
                [32.0, -25.0],
            ]],
        }
    }
    service.repo.get_or_create_dataset.side_effect = lambda dataset: dataset
    service.repo.upsert_indicators.side_effect = lambda records: len(records)

    result = service.ingest_power_daily(
        region_id=run.region_id,
        bounds=(-25.0, -24.0, 32.0, 33.0),
        parameter="T2M",
        start=date(2026, 1, 1),
        end=date(2026, 1, 2),
        community="ag",
    )

    dataset = service.repo.get_or_create_dataset.call_args.args[0]
    records = service.repo.upsert_indicators.call_args.args[0]
    assert isinstance(dataset, Dataset)
    assert dataset.source == "NASA POWER"
    assert dataset.version == "v2.10.3"
    assert dataset.metadata_json["parameter"]["units"] == "C"
    assert dataset.is_synthetic is False
    assert len(records) == 1
    assert records[0]["value"] == 27.1
    assert records[0]["unit"] == "C"
    assert records[0]["latitude"] == -24.5
    assert records[0]["longitude"] == 32.5
    assert records[0]["dataset_id"] == dataset.id
    assert result["records_processed"] == 1
    service.repo.finish_run.assert_called_once()
    assert service.repo.finish_run.call_args.kwargs["status"] == "succeeded"
    assert service.repo.finish_run.call_args.kwargs["version"] == "v2.10.3"


@pytest.mark.anyio
async def test_timeseries_endpoint_returns_dataset_provenance_and_warning() -> None:
    region_id = uuid.uuid4()
    dataset_id = uuid.uuid4()
    indicator_id = uuid.uuid4()
    dataset = Dataset(
        id=dataset_id,
        source="NASA POWER",
        product="POWER Daily Regional",
        variable="T2M",
        version="v2.10.3",
        spatial_resolution="Native source resolution; varies by parameter",
        temporal_resolution="daily",
        quality_notes="Grid data, not a local measurement.",
        metadata_json={"parameter": {"units": "C"}},
        is_synthetic=False,
    )
    indicator = MagicMock()
    indicator.id = indicator_id
    indicator.region_id = region_id
    indicator.dataset_id = dataset_id
    indicator.indicator_type = "T2M"
    indicator.value = 27.1
    indicator.unit = "C"
    indicator.observed_at = date(2026, 1, 1)
    indicator.latitude = -24.5
    indicator.longitude = 32.5
    indicator.category = "derived"
    indicator.is_synthetic = False
    service = MagicMock(spec=EarthObservationService)
    service.list_timeseries.return_value = ([(indicator, dataset)], 1)
    app.dependency_overrides[get_earth_observation_service] = lambda: service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/earth-observation/timeseries",
                params={
                    "region_id": str(region_id),
                    "indicator_type": "T2M",
                    "start": "2026-01-01",
                    "end": "2026-01-02",
                },
            )
    finally:
        app.dependency_overrides.pop(get_earth_observation_service, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"][0]["source"] == "NASA POWER"
    assert payload["items"][0]["dataset_version"] == "v2.10.3"
    assert payload["items"][0]["is_synthetic"] is False
    assert "not measurements of individual fields" in payload["items"][0]["resolution_warning"]
