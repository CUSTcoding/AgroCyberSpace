"""FastAPI router for Region, District, and Community endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.regions.schemas import (
    CommunityListResponse,
    CommunityRead,
    DistrictListResponse,
    DistrictRead,
    GeoJSONFeature,
    RegionIndicatorListResponse,
    RegionIndicatorRead,
    RegionListResponse,
    RegionRead,
)
from app.modules.regions.service import RegionService

router = APIRouter(prefix="/regions", tags=["Regions"])


def get_region_service(db: Annotated[Session, Depends(get_db)]) -> RegionService:
    """Dependency provider for RegionService."""
    return RegionService(db)


@router.get(
    "",
    response_model=RegionListResponse,
    summary="List all study regions",
    description="Retrieve all proposed agricultural study regions with pagination.",
)
def list_regions(
    service: Annotated[RegionService, Depends(get_region_service)],
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    offset: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
) -> RegionListResponse:
    """List study regions."""
    items, total = service.list_regions(limit=limit, offset=offset)
    return RegionListResponse(
        items=[RegionRead.model_validate(r) for r in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{region_id}",
    response_model=RegionRead,
    summary="Get region details",
    description="Retrieve details for a specific study region by its UUID.",
)
def get_region(
    region_id: uuid.UUID,
    service: Annotated[RegionService, Depends(get_region_service)],
) -> RegionRead:
    """Fetch single region."""
    region = service.get_region(region_id)
    return RegionRead.model_validate(region)


@router.get(
    "/{region_id}/districts",
    response_model=DistrictListResponse,
    summary="List districts in region",
    description="Retrieve administrative districts (CENACARTA 2017) within a specified region.",
)
def list_districts(
    region_id: uuid.UUID,
    service: Annotated[RegionService, Depends(get_region_service)],
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 50,
    offset: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
) -> DistrictListResponse:
    """List districts belonging to a region."""
    items, total = service.list_districts(region_id, limit=limit, offset=offset)
    return DistrictListResponse(
        items=[DistrictRead.model_validate(d) for d in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{region_id}/communities",
    response_model=CommunityListResponse,
    summary="List communities in region",
    description="Retrieve local agricultural communities located in a region's districts.",
)
def list_communities(
    region_id: uuid.UUID,
    service: Annotated[RegionService, Depends(get_region_service)],
    limit: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 50,
    offset: Annotated[int, Query(ge=0, description="Offset for pagination")] = 0,
) -> CommunityListResponse:
    """List communities in a region."""
    items, total = service.list_communities(region_id, limit=limit, offset=offset)
    return CommunityListResponse(
        items=[CommunityRead.model_validate(c) for c in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{region_id}/map",
    response_model=GeoJSONFeature,
    summary="Get region boundary GeoJSON map",
    description=(
        "Retrieve the GeoJSON Feature representing the study region boundary for map rendering."
    ),
)
def get_region_map(
    region_id: uuid.UUID,
    service: Annotated[RegionService, Depends(get_region_service)],
) -> dict[str, Any]:
    """Get GeoJSON feature of region boundary."""
    return service.get_region_map(region_id)


@router.get("/{region_id}/map-config", summary="Get region map configuration")
def get_region_map_config(
    region_id: uuid.UUID,
    service: Annotated[RegionService, Depends(get_region_service)],
) -> dict[str, Any]:
    """Return map bounds and currently available layers for a region."""
    return service.get_map_config(region_id)


@router.get("/{region_id}/indicators", response_model=RegionIndicatorListResponse)
def list_region_indicators(
    region_id: uuid.UUID,
    service: Annotated[RegionService, Depends(get_region_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> RegionIndicatorListResponse:
    """List district-level crop statistics available for this region."""
    items, total = service.list_region_indicators(region_id, limit, offset)
    return RegionIndicatorListResponse(
        items=[RegionIndicatorRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )
