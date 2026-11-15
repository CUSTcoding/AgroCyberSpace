"""Repositories for district crop statistics and national soil units."""

from __future__ import annotations

import json
import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.agriculture.models import DistrictCropStat, SoilUnit
from app.modules.regions.models import District


class DistrictCropStatRepository:
    """Repository for district crop area and production statistics."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_district(self, district_id: uuid.UUID) -> list[DistrictCropStat]:
        """List all crop statistics for a given district."""
        stmt = (
            select(DistrictCropStat)
            .where(DistrictCropStat.district_id == district_id)
            .order_by(DistrictCropStat.area_ha.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_by_region(
        self,
        region_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> list[tuple[DistrictCropStat, str]]:
        """List crop statistics in a region, retaining their district names."""
        stmt = (
            select(DistrictCropStat, District.name)
            .join(District, DistrictCropStat.district_id == District.id)
            .where(District.region_id == region_id)
            .order_by(District.name.asc(), DistrictCropStat.area_ha.desc())
            .limit(limit)
            .offset(offset)
        )
        return [(row[0], row[1]) for row in self.db.execute(stmt).all()]

    def count_by_region(self, region_id: uuid.UUID) -> int:
        """Count crop-stat rows for districts in a region."""
        stmt = (
            select(func.count(DistrictCropStat.id))
            .join(District, DistrictCropStat.district_id == District.id)
            .where(District.region_id == region_id)
        )
        return int(self.db.scalar(stmt) or 0)

    def get_by_district_and_crop(
        self, district_id: uuid.UUID, crop: str
    ) -> DistrictCropStat | None:
        """Find statistics for a specific crop in a district."""
        stmt = select(DistrictCropStat).where(
            DistrictCropStat.district_id == district_id,
            func.lower(DistrictCropStat.crop) == func.lower(crop.strip()),
        )
        return self.db.scalars(stmt).first()

    def get_crops_with_positive_area(self, district_id: uuid.UUID) -> list[str]:
        """Return list of crop names having area_ha > 0 in the district (rule 9)."""
        stmt = (
            select(DistrictCropStat.crop)
            .where(
                DistrictCropStat.district_id == district_id,
                DistrictCropStat.area_ha > 0,
            )
            .order_by(DistrictCropStat.crop.asc())
        )
        return list(self.db.scalars(stmt).all())

    def create(self, stat: DistrictCropStat) -> DistrictCropStat:
        """Persist a new district crop statistic."""
        self.db.add(stat)
        self.db.commit()
        self.db.refresh(stat)
        return stat


class SoilUnitRepository:
    """Repository for national soil classification units."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, soil_unit_id: uuid.UUID) -> SoilUnit | None:
        """Fetch soil unit by UUID."""
        stmt = select(SoilUnit).where(SoilUnit.id == soil_unit_id)
        return self.db.scalars(stmt).first()

    def get_by_code(self, code: str) -> SoilUnit | None:
        """Fetch soil unit by classification code."""
        stmt = select(SoilUnit).where(func.lower(SoilUnit.code) == func.lower(code.strip()))
        return self.db.scalars(stmt).first()

    def list(self) -> list[SoilUnit]:
        """List all national soil units."""
        stmt = select(SoilUnit).order_by(SoilUnit.name.asc())
        return list(self.db.scalars(stmt).all())

    def create(self, unit: SoilUnit) -> SoilUnit:
        """Persist a new soil unit."""
        self.db.add(unit)
        self.db.commit()
        self.db.refresh(unit)
        return unit

    def get_geojson(self, soil_unit_id: uuid.UUID) -> dict[str, Any] | None:
        """Return GeoJSON Feature representation of a soil unit."""
        stmt = select(
            SoilUnit.id,
            SoilUnit.code,
            SoilUnit.name,
            SoilUnit.description,
            SoilUnit.properties,
            SoilUnit.source,
            SoilUnit.year,
            func.ST_AsGeoJSON(SoilUnit.boundary).label("geojson"),
        ).where(SoilUnit.id == soil_unit_id)

        row = self.db.execute(stmt).first()
        if row is None:
            return None

        geom = json.loads(row.geojson) if row.geojson else None
        return {
            "type": "Feature",
            "id": str(row.id),
            "properties": {
                "id": str(row.id),
                "code": row.code,
                "name": row.name,
                "description": row.description,
                "properties": row.properties,
                "source": row.source,
                "year": row.year,
            },
            "geometry": geom,
        }
