"""Persistence operations for Earth Observation datasets and point indicators."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.modules.earth_observation.models import Dataset, Indicator, IngestionRun
from app.modules.regions.repository import RegionRepository


class EarthObservationRepository:
    """Store and query source-versioned environmental data."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_run(self, run: IngestionRun) -> IngestionRun:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def get_region_boundary(self, region_id: uuid.UUID) -> dict[str, Any] | None:
        """Return the stored AOI GeoJSON used to filter incoming grid points."""
        return RegionRepository(self.db).get_geojson(region_id)

    def get_or_create_dataset(self, dataset: Dataset) -> Dataset:
        stmt = select(Dataset).where(
            Dataset.source == dataset.source,
            Dataset.product == dataset.product,
            Dataset.variable == dataset.variable,
            Dataset.version == dataset.version,
        )
        existing = self.db.scalars(stmt).first()
        if existing is not None:
            existing.metadata_json = dataset.metadata_json
            existing.spatial_resolution = dataset.spatial_resolution
            existing.temporal_resolution = dataset.temporal_resolution
            existing.quality_notes = dataset.quality_notes
            existing.license = dataset.license
            self.db.flush()
            return existing
        self.db.add(dataset)
        self.db.flush()
        return dataset

    def upsert_indicators(self, indicators: list[dict[str, Any]]) -> int:
        if not indicators:
            return 0
        stmt = insert(Indicator).values(indicators)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_indicators_dataset_region_point_date",
            set_={
                "value": stmt.excluded.value,
                "unit": stmt.excluded.unit,
                "category": stmt.excluded.category,
                "is_synthetic": stmt.excluded.is_synthetic,
            },
        )
        self.db.execute(stmt)
        return len(indicators)

    def finish_run(
        self,
        run: IngestionRun,
        *,
        status: str,
        dataset_id: uuid.UUID | None = None,
        version: str | None = None,
        checksum: str | None = None,
        error: str | None = None,
    ) -> None:
        run.status = status
        run.dataset_id = dataset_id
        run.version = version
        run.checksum = checksum
        run.error = error
        run.finished_at = datetime.now().astimezone()
        self.db.commit()

    def list_datasets(self, limit: int, offset: int) -> tuple[list[Dataset], int]:
        items = list(
            self.db.scalars(
                select(Dataset).order_by(Dataset.created_at.desc()).limit(limit).offset(offset)
            ).all()
        )
        total = int(self.db.scalar(select(func.count(Dataset.id))) or 0)
        return items, total

    def get_dataset(self, dataset_id: uuid.UUID) -> Dataset | None:
        return self.db.get(Dataset, dataset_id)

    def list_indicators(
        self,
        region_id: uuid.UUID,
        indicator_type: str,
        start: date,
        end: date,
        limit: int,
        offset: int,
    ) -> tuple[list[tuple[Indicator, Dataset]], int]:
        filters = (
            Indicator.region_id == region_id,
            Indicator.indicator_type == indicator_type,
            Indicator.observed_at >= start,
            Indicator.observed_at <= end,
        )
        stmt = (
            select(Indicator, Dataset)
            .join(Dataset, Indicator.dataset_id == Dataset.id)
            .where(*filters)
            .order_by(
                Indicator.observed_at.asc(),
                Indicator.latitude.asc(),
                Indicator.longitude.asc(),
            )
        )
        items = list(self.db.execute(stmt.limit(limit).offset(offset)).all())
        count_stmt = select(func.count(Indicator.id)).where(*filters)
        total = int(self.db.scalar(count_stmt) or 0)
        return [(row[0], row[1]) for row in items], total
