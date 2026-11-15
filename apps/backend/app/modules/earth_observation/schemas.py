"""API schemas for persisted Earth Observation data."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class DatasetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source: str
    product: str
    variable: str
    version: str
    spatial_resolution: str
    temporal_resolution: str
    quality_notes: str
    metadata_json: dict[str, Any]
    license: str | None
    is_synthetic: bool
    created_at: datetime


class DatasetListResponse(BaseModel):
    items: list[DatasetRead]
    total: int
    limit: int
    offset: int


class IndicatorRead(BaseModel):
    id: uuid.UUID
    region_id: uuid.UUID
    dataset_id: uuid.UUID
    indicator_type: str
    value: float
    unit: str
    observed_at: date
    latitude: float
    longitude: float
    category: Literal["observed", "derived", "forecast", "simulation"]
    is_synthetic: bool
    source: str
    dataset_version: str
    spatial_resolution: str
    resolution_warning: str


class IndicatorListResponse(BaseModel):
    items: list[IndicatorRead]
    total: int
    limit: int
    offset: int
    data_as_of: datetime | None
