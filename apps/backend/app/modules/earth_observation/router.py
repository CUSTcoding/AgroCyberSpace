"""Read endpoints for persisted Earth Observation datasets and indicators."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, time
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.earth_observation.schemas import (
    DatasetListResponse,
    DatasetRead,
    IndicatorListResponse,
    IndicatorRead,
)
from app.modules.earth_observation.service import EarthObservationService
from app.shared.exceptions import NotFoundException, ValidationException

router = APIRouter(prefix="/earth-observation", tags=["Earth Observation"])


def get_earth_observation_service(
    db: Annotated[Session, Depends(get_db)],
) -> EarthObservationService:
    return EarthObservationService(db)


@router.get("/datasets", response_model=DatasetListResponse)
def list_datasets(
    service: Annotated[EarthObservationService, Depends(get_earth_observation_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DatasetListResponse:
    items, total = service.list_datasets(limit, offset)
    return DatasetListResponse(
        items=[DatasetRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/metadata/{dataset_id}", response_model=DatasetRead)
def get_dataset_metadata(
    dataset_id: uuid.UUID,
    service: Annotated[EarthObservationService, Depends(get_earth_observation_service)],
) -> DatasetRead:
    dataset = service.get_dataset(dataset_id)
    if dataset is None:
        raise NotFoundException(
            message=f"Dataset '{dataset_id}' was not found.",
            details={"dataset_id": str(dataset_id)},
        )
    return DatasetRead.model_validate(dataset)


@router.get("/indicators", response_model=IndicatorListResponse)
@router.get("/timeseries", response_model=IndicatorListResponse)
def list_indicators(
    region_id: uuid.UUID,
    indicator_type: Annotated[str, Query(min_length=1, max_length=100)],
    start: date,
    end: date,
    service: Annotated[EarthObservationService, Depends(get_earth_observation_service)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> IndicatorListResponse:
    if end < start:
        raise ValidationException("end must be on or after start")
    rows, total = service.list_timeseries(
        region_id=region_id,
        indicator_type=indicator_type,
        start=start,
        end=end,
        limit=limit,
        offset=offset,
    )
    items = [
        IndicatorRead(
            id=indicator.id,
            region_id=indicator.region_id,
            dataset_id=indicator.dataset_id,
            indicator_type=indicator.indicator_type,
            value=indicator.value,
            unit=indicator.unit,
            observed_at=indicator.observed_at,
            latitude=indicator.latitude,
            longitude=indicator.longitude,
            category=indicator.category,
            is_synthetic=indicator.is_synthetic,
            source=dataset.source,
            dataset_version=dataset.version,
            spatial_resolution=dataset.spatial_resolution,
            resolution_warning=(
                "Gridded data are regional context and are not measurements of individual fields."
            ),
        )
        for indicator, dataset in rows
    ]
    data_as_of = max(
        (datetime.combine(item.observed_at, time.min, tzinfo=UTC) for item in items),
        default=None,
    )
    return IndicatorListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        data_as_of=data_as_of,
    )
