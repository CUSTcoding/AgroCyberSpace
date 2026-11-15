"""Service layer for Region, District, and Community domain logic."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.modules.regions.models import Community, District, Region
from app.modules.regions.repository import (
    CommunityRepository,
    DistrictRepository,
    RegionRepository,
)
from app.shared.exceptions import NotFoundException


class RegionService:
    """Orchestrates operations and business rules for regions and national layers."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.region_repo = RegionRepository(db)
        self.district_repo = DistrictRepository(db)
        self.community_repo = CommunityRepository(db)

    def list_regions(self, limit: int = 100, offset: int = 0) -> tuple[list[Region], int]:
        """Return paginated list of all study regions."""
        items = self.region_repo.list(limit=limit, offset=offset)
        total = self.region_repo.count()
        return items, total

    def get_region(self, region_id: uuid.UUID) -> Region:
        """Fetch a specific region by UUID, or raise NotFoundException."""
        region = self.region_repo.get_by_id(region_id)
        if region is None:
            raise NotFoundException(
                message=f"Region with id '{region_id}' was not found.",
                details={"region_id": str(region_id)},
            )
        return region

    def get_region_by_code(self, code: str) -> Region:
        """Fetch a specific region by code (e.g. 'gaza'), or raise NotFoundException."""
        region = self.region_repo.get_by_code(code)
        if region is None:
            raise NotFoundException(
                message=f"Region with code '{code}' was not found.",
                details={"code": code},
            )
        return region

    def list_districts(
        self, region_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> tuple[list[District], int]:
        """Return paginated list of administrative districts for a verified region."""
        # Ensure region exists
        self.get_region(region_id)
        items = self.district_repo.list_by_region(region_id, limit=limit, offset=offset)
        total = self.district_repo.count_by_region(region_id)
        return items, total

    def list_communities(
        self, region_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> tuple[list[Community], int]:
        """Return paginated list of communities across all districts in a region."""
        # Ensure region exists
        self.get_region(region_id)
        items = self.community_repo.list_by_region(region_id, limit=limit, offset=offset)
        total = self.community_repo.count_by_region(region_id)
        return items, total

    def get_region_map(self, region_id: uuid.UUID) -> dict[str, Any]:
        """Return the GeoJSON Feature representing the region's boundary."""
        # Ensure region exists
        self.get_region(region_id)
        feature = self.region_repo.get_geojson(region_id)
        if feature is None:
            raise NotFoundException(
                message=f"Boundary geometry for region '{region_id}' is not available.",
                details={"region_id": str(region_id)},
            )
        return feature
