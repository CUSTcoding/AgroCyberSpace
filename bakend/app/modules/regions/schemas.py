"""Pydantic v2 validation and serialization schemas for Regions, Districts, and Communities."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RegionBase(BaseModel):
    """Base schema for study region."""

    code: str = Field(..., max_length=50, description="Unique region identifier code")
    name: str = Field(..., max_length=100, description="Display name of the region")
    description: str | None = Field(None, description="Detailed study area description")
    is_proposed_study_area: bool = Field(
        True,
        description=(
            "Scientific flag indicating this is a proposed study area, not a validated boundary"
        ),
    )


class RegionRead(RegionBase):
    """Schema for returning region details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class RegionListResponse(BaseModel):
    """Paginated list of study regions."""

    items: list[RegionRead]
    total: int
    limit: int
    offset: int


class DistrictBase(BaseModel):
    """Base schema for administrative district."""

    code: str = Field(..., max_length=50, description="Unique district code")
    name: str = Field(..., max_length=100, description="Display name of the district")
    province: str = Field(..., max_length=100, description="Province name")
    source: str = Field("CENACARTA 2017", description="Source boundary dataset")


class DistrictRead(DistrictBase):
    """Schema for returning district details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    region_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DistrictListResponse(BaseModel):
    """Paginated list of districts."""

    items: list[DistrictRead]
    total: int
    limit: int
    offset: int


class CommunityBase(BaseModel):
    """Base schema for local community."""

    name: str = Field(..., max_length=100, description="Community or settlement name")
    description: str | None = Field(None, description="Agronomic or local description")


class CommunityRead(CommunityBase):
    """Schema for returning community details."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    district_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CommunityListResponse(BaseModel):
    """Paginated list of communities."""

    items: list[CommunityRead]
    total: int
    limit: int
    offset: int


class GeoJSONFeature(BaseModel):
    """RFC 7946 GeoJSON Feature format."""

    type: str = Field("Feature", description="GeoJSON type")
    id: str = Field(..., description="Entity UUID")
    properties: dict[str, Any] = Field(..., description="Feature properties")
    geometry: dict[str, Any] | None = Field(None, description="Geometry coordinates in EPSG:4326")
