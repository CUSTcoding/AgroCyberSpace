"""Repository layer for Region, District, and Community geospatial database operations."""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.regions.models import Community, District, Region


class RegionRepository:
    """Database repository for Region entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, region_id: uuid.UUID) -> Region | None:
        """Find a region by its unique UUID."""
        stmt = select(Region).where(Region.id == region_id)
        return self.db.scalars(stmt).first()

    def get_by_code(self, code: str) -> Region | None:
        """Find a region by its unique string code (e.g. 'gaza')."""
        stmt = select(Region).where(func.lower(Region.code) == func.lower(code.strip()))
        return self.db.scalars(stmt).first()

    def list(self, limit: int = 100, offset: int = 0) -> list[Region]:
        """List study regions with pagination."""
        stmt = select(Region).order_by(Region.name.asc()).limit(limit).offset(offset)
        return list(self.db.scalars(stmt).all())

    def count(self) -> int:
        """Total count of regions."""
        stmt = select(func.count(Region.id))
        result = self.db.execute(stmt).scalar()
        return int(result or 0)

    def create(self, region: Region) -> Region:
        """Persist a new region entity."""
        self.db.add(region)
        self.db.commit()
        self.db.refresh(region)
        return region

    def get_geojson(self, region_id: uuid.UUID) -> dict[str, Any] | None:
        """Return the GeoJSON Feature of a region boundary using PostGIS ST_AsGeoJSON."""
        stmt = select(
            Region.id,
            Region.code,
            Region.name,
            Region.description,
            Region.is_proposed_study_area,
            func.ST_AsGeoJSON(Region.boundary).label("geojson"),
        ).where(Region.id == region_id)

        row = self.db.execute(stmt).first()
        if row is None:
            return None

        geometry = json.loads(row.geojson) if row.geojson else None
        return {
            "type": "Feature",
            "id": str(row.id),
            "properties": {
                "id": str(row.id),
                "code": row.code,
                "name": row.name,
                "description": row.description,
                "is_proposed_study_area": row.is_proposed_study_area,
            },
            "geometry": geometry,
        }


class DistrictRepository:
    """Database repository for District entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, district_id: uuid.UUID) -> District | None:
        """Find a district by its UUID."""
        stmt = select(District).where(District.id == district_id)
        return self.db.scalars(stmt).first()

    def get_by_code(self, code: str) -> District | None:
        """Find a district by its code (e.g. 'chokwe')."""
        stmt = select(District).where(func.lower(District.code) == func.lower(code.strip()))
        return self.db.scalars(stmt).first()

    def list_by_region(
        self, region_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> list[District]:
        """List districts belonging to a region with pagination."""
        stmt = (
            select(District)
            .where(District.region_id == region_id)
            .order_by(District.name.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt).all())

    def count_by_region(self, region_id: uuid.UUID) -> int:
        """Total count of districts in a region."""
        stmt = select(func.count(District.id)).where(District.region_id == region_id)
        result = self.db.execute(stmt).scalar()
        return int(result or 0)

    def create(self, district: District) -> District:
        """Persist a new district entity."""
        self.db.add(district)
        self.db.commit()
        self.db.refresh(district)
        return district

    def get_geojson(self, district_id: uuid.UUID) -> dict[str, Any] | None:
        """Return the GeoJSON Feature of a district boundary."""
        stmt = select(
            District.id,
            District.region_id,
            District.code,
            District.name,
            District.province,
            District.source,
            func.ST_AsGeoJSON(District.boundary).label("geojson"),
        ).where(District.id == district_id)

        row = self.db.execute(stmt).first()
        if row is None:
            return None

        geometry = json.loads(row.geojson) if row.geojson else None
        return {
            "type": "Feature",
            "id": str(row.id),
            "properties": {
                "id": str(row.id),
                "region_id": str(row.region_id),
                "code": row.code,
                "name": row.name,
                "province": row.province,
                "source": row.source,
            },
            "geometry": geometry,
        }


class CommunityRepository:
    """Database repository for Community entities."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, community_id: uuid.UUID) -> Community | None:
        """Find a community by its UUID."""
        stmt = select(Community).where(Community.id == community_id)
        return self.db.scalars(stmt).first()

    def list_by_district(
        self, district_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> list[Community]:
        """List communities in a district with pagination."""
        stmt = (
            select(Community)
            .where(Community.district_id == district_id)
            .order_by(Community.name.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt).all())

    def list_by_region(
        self, region_id: uuid.UUID, limit: int = 100, offset: int = 0
    ) -> list[Community]:
        """List all communities in all districts of a region."""
        stmt = (
            select(Community)
            .join(District, Community.district_id == District.id)
            .where(District.region_id == region_id)
            .order_by(Community.name.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.scalars(stmt).all())

    def count_by_region(self, region_id: uuid.UUID) -> int:
        """Count all communities belonging to districts of a region."""
        stmt = (
            select(func.count(Community.id))
            .join(District, Community.district_id == District.id)
            .where(District.region_id == region_id)
        )
        result = self.db.execute(stmt).scalar()
        return int(result or 0)

    def create(self, community: Community) -> Community:
        """Persist a new community entity."""
        self.db.add(community)
        self.db.commit()
        self.db.refresh(community)
        return community
