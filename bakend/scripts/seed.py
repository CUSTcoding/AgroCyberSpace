"""Idempotent seed script for loading initial study regions, districts, and communities."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from geoalchemy2.shape import from_shape
from shapely.geometry import Point, shape
from sqlalchemy.orm import Session

from app.core.database import get_session_factory
from app.modules.regions.models import Community, District, Region
from app.modules.regions.repository import (
    CommunityRepository,
    DistrictRepository,
    RegionRepository,
)

logger = logging.getLogger(__name__)

SEEDS_AOI_DIR = Path(__file__).resolve().parent.parent / "seeds" / "aoi"

# Initial seed registry for confirmed districts and communities
CONFIRMED_DATA: dict[str, dict[str, Any]] = {
    "gaza": {
        "districts": [
            {
                "code": "chokwe",
                "name": "Chókwè",
                "province": "Gaza",
                "source": "CENACARTA 2017",
                "communities": [
                    {
                        "name": "Lionde",
                        "description": "Zona agrícola central do regadio de Chókwè",
                        "lon": 33.05,
                        "lat": -24.52,
                    },
                    {
                        "name": "Conhane",
                        "description": "Zona de produção hortícola e cereais",
                        "lon": 33.00,
                        "lat": -24.45,
                    },
                ],
            },
            {
                "code": "guija",
                "name": "Guijá",
                "province": "Gaza",
                "source": "CENACARTA 2017",
                "communities": [
                    {
                        "name": "Caniçado",
                        "description": "Margem norte do Rio Limpopo",
                        "lon": 33.02,
                        "lat": -24.50,
                    }
                ],
            },
        ]
    },
    "zambezia": {
        "districts": [
            {
                "code": "mocuba",
                "name": "Mocuba",
                "province": "Zambézia",
                "source": "CENACARTA 2017",
                "communities": [
                    {
                        "name": "Mocuba-Sede",
                        "description": "Área de influência agrícola da bacia do Licungo",
                        "lon": 36.98,
                        "lat": -16.84,
                    },
                    {
                        "name": "Mugeba",
                        "description": "Zona de transição agro-ecológica e culturas de sequeiro",
                        "lon": 37.10,
                        "lat": -16.95,
                    },
                ],
            },
            {
                "code": "lugela",
                "name": "Lugela",
                "province": "Zambézia",
                "source": "CENACARTA 2017",
                "communities": [
                    {
                        "name": "Lugela-Sede",
                        "description": "Vale alto do Licungo e encostas agrícolas",
                        "lon": 36.98,
                        "lat": -16.22,
                    }
                ],
            },
        ]
    },
    "tete": {
        "districts": [
            {
                "code": "angonia",
                "name": "Angónia",
                "province": "Tete",
                "source": "CENACARTA 2017",
                "communities": [
                    {
                        "name": "Ulongué",
                        "description": (
                            "Planalto fértil de Angónia, polo de produção de milho e batata"
                        ),
                        "lon": 34.36,
                        "lat": -14.72,
                    },
                    {
                        "name": "Domué",
                        "description": "Zona agrícola de altitude e clima temperado",
                        "lon": 34.22,
                        "lat": -14.48,
                    },
                ],
            },
            {
                "code": "tsangano",
                "name": "Tsangano",
                "province": "Tete",
                "source": "CENACARTA 2017",
                "communities": [
                    {
                        "name": "Tsangano-Sede",
                        "description": "Área de expansão agrícola e rotação de leguminosas",
                        "lon": 34.48,
                        "lat": -15.12,
                    }
                ],
            },
        ]
    },
}


def load_aoi_geojson(file_path: Path) -> dict[str, Any]:
    """Read and parse an AOI GeoJSON file."""
    with file_path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
        return data


def seed_regions_and_districts(db: Session, aoi_dir: Path = SEEDS_AOI_DIR) -> dict[str, int]:
    """Idempotently seed confirmed study regions, districts, and communities from GeoJSON AOIs."""
    region_repo = RegionRepository(db)
    district_repo = DistrictRepository(db)
    community_repo = CommunityRepository(db)

    stats = {"regions_seeded": 0, "districts_seeded": 0, "communities_seeded": 0}

    # Find all confirmed GeoJSON AOI definitions
    geojson_files = sorted(aoi_dir.glob("*.geojson"))
    if not geojson_files:
        logger.warning("No AOI GeoJSON files found in %s", aoi_dir)
        return stats

    for geo_file in geojson_files:
        data = load_aoi_geojson(geo_file)
        features = data.get("features", [])
        if not features:
            continue

        feature = features[0]
        props = feature.get("properties", {})
        code = str(props.get("code", geo_file.stem)).lower().strip()
        name = str(props.get("name", code.capitalize()))
        description = props.get("description")
        is_proposed = bool(props.get("is_proposed_study_area", True))

        # Convert GeoJSON geometry to PostGIS element via Shapely
        geom_dict = feature.get("geometry")
        boundary_geom = None
        if geom_dict:
            shapely_geom = shape(geom_dict)
            boundary_geom = from_shape(shapely_geom, srid=4326)

        # 1. Upsert Region
        region = region_repo.get_by_code(code)
        if region is None:
            region = Region(
                code=code,
                name=name,
                description=description,
                boundary=boundary_geom,
                is_proposed_study_area=is_proposed,
            )
            region = region_repo.create(region)
            stats["regions_seeded"] += 1
            logger.info("Created Region: %s (%s)", region.name, region.code)
        else:
            region.name = name
            region.description = description
            region.boundary = boundary_geom
            region.is_proposed_study_area = is_proposed
            db.commit()
            db.refresh(region)
            logger.info("Updated existing Region: %s (%s)", region.name, region.code)

        # 2. Seed Districts and Communities for this Region if defined
        region_data = CONFIRMED_DATA.get(code)
        if not region_data:
            continue

        districts_data = region_data.get("districts", [])
        for dist_data in districts_data:
            dist_code = dist_data["code"]
            dist_name = dist_data["name"]
            dist_province = dist_data["province"]
            dist_source = dist_data.get("source", "CENACARTA 2017")

            district = district_repo.get_by_code(dist_code)
            if district is None:
                district = District(
                    region_id=region.id,
                    code=dist_code,
                    name=dist_name,
                    province=dist_province,
                    boundary=boundary_geom,  # Associates study area boundary with primary district
                    source=dist_source,
                )
                district = district_repo.create(district)
                stats["districts_seeded"] += 1
                logger.info("Created District: %s under %s", district.name, region.name)
            else:
                district.region_id = region.id
                district.name = dist_name
                district.province = dist_province
                district.source = dist_source
                db.commit()
                db.refresh(district)

            # 3. Seed Communities
            comm_list = dist_data.get("communities", [])
            existing_comms = {
                c.name.lower(): c for c in community_repo.list_by_district(district.id)
            }
            for comm_data in comm_list:
                c_name = comm_data["name"]
                c_desc = comm_data.get("description")
                c_lon = comm_data.get("lon")
                c_lat = comm_data.get("lat")

                point_geom = None
                if c_lon is not None and c_lat is not None:
                    point_geom = from_shape(Point(c_lon, c_lat), srid=4326)

                if c_name.lower() not in existing_comms:
                    community = Community(
                        district_id=district.id,
                        name=c_name,
                        location=point_geom,
                        description=c_desc,
                    )
                    community_repo.create(community)
                    stats["communities_seeded"] += 1
                    logger.info("Created Community: %s under District %s", c_name, district.name)

    return stats


def main() -> None:
    """CLI entrypoint for executing seed script."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger.info("Starting database seed for confirmed study regions...")
    session_factory = get_session_factory()
    db = session_factory()
    try:
        results = seed_regions_and_districts(db)
        logger.info("Seeding completed successfully: %s", results)
    finally:
        db.close()


if __name__ == "__main__":
    main()
