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
from app.modules.agriculture.models import DistrictCropStat, SoilUnit
from app.modules.agriculture.repository import (
    DistrictCropStatRepository,
    SoilUnitRepository,
)
from app.modules.game.models import (
    Chapter,
    Lesson,
    Mission,
    RegionContentStatus,
)
from app.modules.game.repository import (
    ChapterRepository,
    LessonRepository,
    MissionRepository,
    RegionContentStatusRepository,
)
from app.modules.regions.models import Community, District, Region
from app.modules.regions.repository import (
    CommunityRepository,
    DistrictRepository,
    RegionRepository,
)

logger = logging.getLogger(__name__)

SEEDS_AOI_DIR = Path(__file__).resolve().parent.parent / "seeds" / "aoi"
SEEDS_AGRICULTURE_DIR = Path(__file__).resolve().parent.parent / "seeds" / "agriculture"
SEEDS_CONTENT_DIR = Path(__file__).resolve().parent.parent / "seeds" / "content"

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


def seed_crop_stats(
    db: Session,
    file_path: Path = SEEDS_AGRICULTURE_DIR / "crop_stats.json",
) -> int:
    """Seed district crop statistics from JSON."""
    if not file_path.exists():
        logger.warning("Crop stats seed file not found: %s", file_path)
        return 0

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    district_repo = DistrictRepository(db)
    crop_stat_repo = DistrictCropStatRepository(db)
    count = 0

    for item in data:
        dist_code = item["district_code"]
        district = district_repo.get_by_code(dist_code)
        if district is None:
            logger.warning("District '%s' not found for crop stat, skipping", dist_code)
            continue

        crop = item["crop"]
        existing = crop_stat_repo.get_by_district_and_crop(district.id, crop)
        if existing is None:
            stat = DistrictCropStat(
                district_id=district.id,
                crop=crop,
                area_ha=float(item.get("area_ha", 0.0)),
                production_t=float(item.get("production_t", 0.0)),
                campaign=item.get("campaign", "2023/2024"),
                year=int(item.get("year", 2023)),
                source=item.get("source", "INE/MADER - CAP 2023/2024"),
            )
            crop_stat_repo.create(stat)
            count += 1
            logger.info("Created CropStat: %s (%s ha) in %s", crop, stat.area_ha, district.name)
        else:
            existing.area_ha = float(item.get("area_ha", 0.0))
            existing.production_t = float(item.get("production_t", 0.0))
            existing.campaign = item.get("campaign", "2023/2024")
            existing.year = int(item.get("year", 2023))
            existing.source = item.get("source", "INE/MADER - CAP 2023/2024")
            db.commit()
            db.refresh(existing)

    return count


def seed_soil_units(
    db: Session,
    file_path: Path = SEEDS_AGRICULTURE_DIR / "soil_units.json",
) -> int:
    """Seed national soil units (INIA 1995) from JSON."""
    if not file_path.exists():
        logger.warning("Soil units seed file not found: %s", file_path)
        return 0

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    soil_repo = SoilUnitRepository(db)
    count = 0

    for item in data:
        code = item["code"]
        name = item["name"]
        description = item.get("description")
        properties = item.get("properties", {})
        source = item.get("source", "INIA/IIAM 1995")
        year = int(item.get("year", 1995))

        geom_dict = item.get("geometry")
        boundary_geom = None
        if geom_dict:
            shapely_geom = shape(geom_dict)
            boundary_geom = from_shape(shapely_geom, srid=4326)

        existing = soil_repo.get_by_code(code)
        if existing is None:
            unit = SoilUnit(
                code=code,
                name=name,
                description=description,
                properties=properties,
                source=source,
                year=year,
                boundary=boundary_geom,
            )
            soil_repo.create(unit)
            count += 1
            logger.info("Created SoilUnit: %s (%s)", name, code)
        else:
            existing.name = name
            existing.description = description
            existing.properties = properties
            existing.source = source
            existing.year = year
            existing.boundary = boundary_geom
            db.commit()
            db.refresh(existing)

    return count


def seed_chapters_and_content(
    db: Session,
    content_dir: Path = SEEDS_CONTENT_DIR,
) -> dict[str, int]:
    """Idempotently seed all 12 chapters, lessons, missions, and region content statuses."""
    chapter_repo = ChapterRepository(db)
    lesson_repo = LessonRepository(db)
    mission_repo = MissionRepository(db)
    region_repo = RegionRepository(db)
    status_repo = RegionContentStatusRepository(db)

    stats = {
        "chapters_seeded": 0,
        "lessons_seeded": 0,
        "missions_seeded": 0,
        "statuses_seeded": 0,
    }

    if not content_dir.exists():
        logger.warning("Content directory not found: %s", content_dir)
        return stats

    json_files = sorted(content_dir.glob("*/*.json"))
    for file_path in json_files:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        ch_num = int(data["chapter_number"])
        title = data["title"]
        objective = data["learning_objective"]
        is_common = bool(data.get("is_common", False))
        topics = data.get("topics", [])
        provisional = bool(data.get("provisional", True))
        region_code = data.get("region_code")

        # 1. Upsert Chapter
        chapter = chapter_repo.get_by_number(ch_num)
        if chapter is None:
            chapter = Chapter(
                chapter_number=ch_num,
                title=title,
                learning_objective=objective,
                is_common=is_common,
                topics=topics,
                provisional=provisional,
            )
            chapter_repo.create(chapter)
            stats["chapters_seeded"] += 1
            logger.info("Created Chapter #%d: %s", ch_num, title)
        else:
            chapter.title = title
            chapter.learning_objective = objective
            chapter.is_common = is_common
            chapter.topics = topics
            chapter.provisional = provisional
            db.commit()
            db.refresh(chapter)

        # Determine target region if regional content
        target_region = None
        if not is_common and region_code and region_code != "common":
            target_region = region_repo.get_by_code(region_code)

        region_id = target_region.id if target_region else None

        # 2. Seed Lessons
        lessons_data = data.get("lessons", [])
        existing_lessons = {
            (les.position, les.title.lower()): les
            for les in lesson_repo.list_by_chapter_and_region(chapter.id, region_id)
        }
        for l_data in lessons_data:
            pos = int(l_data.get("position", 1))
            l_title = l_data["title"]
            key = (pos, l_title.lower())
            if key not in existing_lessons:
                lesson = Lesson(
                    chapter_id=chapter.id,
                    region_id=region_id,
                    position=pos,
                    topic=l_data["topic"],
                    title=l_title,
                    text_simple=l_data["text_simple"],
                    audio_text=l_data["audio_text"],
                    learning_points=l_data.get("learning_points", []),
                    evidence=l_data.get("evidence", {}),
                    source=l_data["source"],
                    verified=bool(l_data.get("verified", False)),
                    is_synthetic=bool(l_data.get("is_synthetic", False)),
                    language=l_data.get("language", "pt"),
                )
                lesson_repo.create(lesson)
                stats["lessons_seeded"] += 1
                logger.info("Created Lesson: %s (ch=%d)", l_title, ch_num)

        # 3. Seed Missions
        missions_data = data.get("missions", [])
        existing_missions = {
            (m.position, m.title.lower()): m
            for m in mission_repo.list_by_chapter_and_region(chapter.id, region_id)
        }
        for m_data in missions_data:
            pos = int(m_data.get("position", 1))
            m_title = m_data["title"]
            key = (pos, m_title.lower())
            if key not in existing_missions:
                mission = Mission(
                    chapter_id=chapter.id,
                    region_id=region_id,
                    position=pos,
                    mission_type=m_data["mission_type"],
                    title=m_title,
                    prompt_simple=m_data["prompt_simple"],
                    learning_note=m_data["learning_note"],
                    max_score=int(m_data.get("max_score", 100)),
                    configuration=m_data.get("configuration", {}),
                    answer_rules=m_data.get("answer_rules", {}),
                    verified=bool(m_data.get("verified", False)),
                    is_synthetic=bool(m_data.get("is_synthetic", False)),
                    language=m_data.get("language", "pt"),
                )
                mission_repo.create(mission)
                stats["missions_seeded"] += 1
                logger.info("Created Mission: %s (ch=%d)", m_title, ch_num)

        # 4. Upsert RegionContentStatus if target region exists
        if target_region is not None:
            status_obj = status_repo.get_status(target_region.id, chapter.id)
            if status_obj is None:
                status_obj = RegionContentStatus(
                    region_id=target_region.id,
                    chapter_id=chapter.id,
                    lessons_total=len(lessons_data),
                    lessons_verified=sum(1 for les in lessons_data if les.get("verified")),
                    missions_total=len(missions_data),
                    status="draft",
                )
                status_repo.save(status_obj)
                stats["statuses_seeded"] += 1
            else:
                status_obj.lessons_total = len(lessons_data)
                status_obj.lessons_verified = sum(1 for les in lessons_data if les.get("verified"))
                status_obj.missions_total = len(missions_data)
                status_repo.save(status_obj)

    return stats


def main() -> None:
    """CLI entrypoint for executing seed script."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger.info("Starting database seed for confirmed study regions...")
    session_factory = get_session_factory()
    db = session_factory()
    try:
        results = seed_regions_and_districts(db)
        crop_count = seed_crop_stats(db)
        soil_count = seed_soil_units(db)
        content_stats = seed_chapters_and_content(db)
        results["crop_stats_seeded"] = crop_count
        results["soil_units_seeded"] = soil_count
        results.update(content_stats)
        logger.info("Seeding completed successfully: %s", results)
    finally:
        db.close()


if __name__ == "__main__":
    main()
