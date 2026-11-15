"""Earth Observation ingestion orchestration and read API service."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, date, datetime
from typing import Any

from shapely.geometry import Point, shape
from sqlalchemy.orm import Session

from app.modules.earth_observation.models import Dataset, IngestionRun
from app.modules.earth_observation.repository import EarthObservationRepository
from scripts.ingestion.nasa_power import NasaPowerClient, NasaPowerError

NASA_POWER_DOCS = "https://power.larc.nasa.gov/docs/services/api/temporal/daily/"


class EarthObservationService:
    """Ingest and serve stored environmental data without request-time fetching."""

    def __init__(self, db: Session, client: NasaPowerClient | None = None) -> None:
        self.db = db
        self.repo = EarthObservationRepository(db)
        self.client = client

    def ingest_power_daily(
        self,
        *,
        region_id: uuid.UUID,
        bounds: tuple[float, float, float, float],
        parameter: str,
        start: date,
        end: date,
        community: str,
    ) -> dict[str, Any]:
        """Fetch, persist, and audit one NASA POWER regional parameter request."""
        latitude_min, latitude_max, longitude_min, longitude_max = bounds
        run = self.repo.create_run(
            IngestionRun(
                region_id=region_id,
                source="NASA POWER",
                product="POWER Daily Regional",
                time_start=start,
                time_end=end,
                status="running",
            )
        )
        client = self.client or NasaPowerClient()
        try:
            payload = client.fetch_daily_regional(
                parameter=parameter,
                latitude_min=latitude_min,
                latitude_max=latitude_max,
                longitude_min=longitude_min,
                longitude_max=longitude_max,
                start=start,
                end=end,
                community=community,
            )
            unit, parsed_values = NasaPowerClient.parse_regional_response(
                payload,
                parameter=parameter,
                fill_value=float(payload.get("header", {}).get("fill_value", -999)),
            )
            region_feature = self.repo.get_region_boundary(region_id)
            geometry = region_feature.get("geometry") if region_feature is not None else None
            if geometry is None:
                raise ValueError("The region has no boundary geometry for AOI point filtering.")
            aoi = shape(geometry)
            parsed_values = [
                point
                for point in parsed_values
                if aoi.covers(Point(point["longitude"], point["latitude"]))
            ]
            if not parsed_values:
                raise NasaPowerError("NASA POWER returned no grid points inside the region AOI.")
            api_version = str(payload.get("header", {}).get("api", {}).get("version", "unknown"))
            parameter_details = payload["parameters"][parameter]
            metadata = {
                "documentation_url": NASA_POWER_DOCS,
                "api_version": api_version,
                "request": {
                    "parameter": parameter,
                    "community": community,
                    "bounds": list(bounds),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "time_standard": "UTC",
                },
                "parameter": parameter_details,
                "response_header": payload.get("header", {}),
                "messages": payload.get("messages", []),
            }
            dataset = self.repo.get_or_create_dataset(
                Dataset(
                    source="NASA POWER",
                    product="POWER Daily Regional",
                    variable=parameter,
                    version=api_version,
                    spatial_resolution="Native source resolution; varies by parameter",
                    temporal_resolution="daily",
                    quality_notes=(
                        "NASA POWER gridded analysis-ready meteorological/solar data; "
                        "not a local station measurement or parcel observation."
                    ),
                    metadata_json=metadata,
                    license="NASA POWER; redistribution terms require separate verification",
                    is_synthetic=False,
                )
            )
            records = [
                {
                    "id": uuid.uuid4(),
                    "region_id": region_id,
                    "dataset_id": dataset.id,
                    "indicator_type": parameter,
                    "value": item["value"],
                    "unit": unit,
                    "observed_at": item["observed_at"],
                    "latitude": item["latitude"],
                    "longitude": item["longitude"],
                    "category": "derived",
                    "is_synthetic": False,
                }
                for item in parsed_values
            ]
            checksum_payload = [
                {key: value for key, value in record.items() if key != "id"} for record in records
            ]
            checksum = hashlib.sha256(
                json.dumps(checksum_payload, default=str, sort_keys=True).encode("utf-8")
            ).hexdigest()
            saved_count = self.repo.upsert_indicators(records)
            self.repo.finish_run(
                run,
                status="succeeded",
                dataset_id=dataset.id,
                version=api_version,
                checksum=checksum,
            )
            return {
                "run_id": run.id,
                "dataset_id": dataset.id,
                "records_processed": saved_count,
                "unit": unit,
                "api_version": api_version,
            }
        except Exception as err:
            self.db.rollback()
            run.status = "failed"
            run.error = str(err)[:4000]
            run.finished_at = datetime.now(UTC)
            self.db.add(run)
            self.db.commit()
            raise
        finally:
            if self.client is None:
                client.client.close()

    def list_datasets(self, limit: int, offset: int) -> tuple[list[Dataset], int]:
        return self.repo.list_datasets(limit, offset)

    def get_dataset(self, dataset_id: uuid.UUID) -> Dataset | None:
        return self.repo.get_dataset(dataset_id)

    def list_timeseries(
        self,
        *,
        region_id: uuid.UUID,
        indicator_type: str,
        start: date,
        end: date,
        limit: int,
        offset: int,
    ) -> tuple[list[tuple[Any, Dataset]], int]:
        return self.repo.list_indicators(region_id, indicator_type, start, end, limit, offset)
