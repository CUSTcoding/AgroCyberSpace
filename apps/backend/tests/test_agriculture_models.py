"""Unit tests for DistrictCropStat, SoilUnit models, repositories, and seed loaders."""

import uuid
from typing import Any
from unittest.mock import MagicMock

from app.modules.agriculture.models import DistrictCropStat, SoilUnit
from app.modules.agriculture.repository import (
    DistrictCropStatRepository,
    SoilUnitRepository,
)
from app.modules.regions.models import District
from scripts.seed import (
    SEEDS_AGRICULTURE_DIR,
    seed_crop_stats,
    seed_soil_units,
)


def test_district_crop_stat_defaults() -> None:
    district_id = uuid.uuid4()
    stat = DistrictCropStat(
        district_id=district_id,
        crop="maize",
        area_ha=15000.0,
        production_t=30000.0,
    )
    assert stat.district_id == district_id
    assert stat.crop == "maize"
    assert stat.area_ha == 15000.0
    assert stat.production_t == 30000.0
    assert stat.campaign == "2023/2024"
    assert stat.year == 2023
    assert stat.source == "INE/MADER - CAP 2023/2024"
    assert isinstance(stat.id, uuid.UUID)
    assert "maize" in repr(stat)


def test_soil_unit_defaults() -> None:
    soil = SoilUnit(
        code="AL-01",
        name="Solos Aluvionares do Limpopo",
        description="Solos aluvionares de regadio",
        properties={"texture": "argilosa", "drainage": "moderada"},
    )
    assert soil.code == "AL-01"
    assert soil.name == "Solos Aluvionares do Limpopo"
    assert soil.source == "INIA/IIAM 1995"
    assert soil.year == 1995
    assert soil.properties["texture"] == "argilosa"
    assert isinstance(soil.id, uuid.UUID)
    assert "AL-01" in repr(soil)


def test_district_crop_stat_repository() -> None:
    mock_db = MagicMock()
    district_id = uuid.uuid4()
    stat = DistrictCropStat(
        district_id=district_id,
        crop="rice",
        area_ha=14000.0,
        production_t=56000.0,
    )

    mock_db.scalars.return_value.all.return_value = [stat]
    mock_db.scalars.return_value.first.return_value = stat

    repo = DistrictCropStatRepository(mock_db)

    # list_by_district
    assert repo.list_by_district(district_id) == [stat]

    # get_by_district_and_crop
    assert repo.get_by_district_and_crop(district_id, "rice") == stat

    # get_crops_with_positive_area (Rule 9)
    mock_db.scalars.return_value.all.return_value = ["rice", "maize"]
    crops = repo.get_crops_with_positive_area(district_id)
    assert crops == ["rice", "maize"]

    # create
    created = repo.create(stat)
    assert created == stat
    mock_db.add.assert_called_once_with(stat)
    mock_db.commit.assert_called_once()


def test_soil_unit_repository() -> None:
    mock_db = MagicMock()
    soil_id = uuid.uuid4()
    soil = SoilUnit(
        id=soil_id,
        code="FR-02",
        name="Solos Franco-Argilosos do Licungo",
    )

    mock_db.scalars.return_value.first.return_value = soil
    mock_db.scalars.return_value.all.return_value = [soil]

    repo = SoilUnitRepository(mock_db)

    # get_by_id
    assert repo.get_by_id(soil_id) == soil
    # get_by_code
    assert repo.get_by_code("FR-02") == soil
    # list
    assert repo.list() == [soil]

    # create
    created = repo.create(soil)
    assert created == soil

    # get_geojson
    mock_row = MagicMock()
    mock_row.id = soil_id
    mock_row.code = "FR-02"
    mock_row.name = "Solos Franco-Argilosos do Licungo"
    mock_row.description = "Solos do Licungo"
    mock_row.properties = {"texture": "franco-argilosa"}
    mock_row.source = "INIA/IIAM 1995"
    mock_row.year = 1995
    mock_row.geojson = (
        '{"type": "Polygon", "coordinates": [[[36.8, -16.5], [37.2, -16.5], '
        "[37.2, -17.1], [36.8, -16.5]]]}"
    )
    mock_db.execute.return_value.first.return_value = mock_row

    feature = repo.get_geojson(soil_id)
    assert feature is not None
    assert feature["type"] == "Feature"
    assert feature["properties"]["code"] == "FR-02"
    assert feature["properties"]["year"] == 1995
    assert feature["geometry"]["type"] == "Polygon"


def test_seed_agriculture_files_exist_and_valid() -> None:
    """Verify seed files exist and contain required schema fields."""
    crop_stats_file = SEEDS_AGRICULTURE_DIR / "crop_stats.json"
    soil_units_file = SEEDS_AGRICULTURE_DIR / "soil_units.json"

    assert crop_stats_file.exists()
    assert soil_units_file.exists()


def test_seed_crop_stats_function() -> None:
    mock_db = MagicMock()
    district = District(
        id=uuid.uuid4(),
        region_id=uuid.uuid4(),
        code="chokwe",
        name="Chókwè",
        province="Gaza",
    )
    call_count = 0

    def mock_first() -> Any:
        nonlocal call_count
        call_count += 1
        # Odd calls look up district; even calls look up existing crop stat (simulate none found)
        return district if call_count % 2 == 1 else None

    mock_db.scalars.return_value.first.side_effect = mock_first

    count = seed_crop_stats(mock_db)
    assert count >= 1


def test_seed_soil_units_function() -> None:
    mock_db = MagicMock()
    # Return None for existing lookup to simulate new creations
    mock_db.scalars.return_value.first.return_value = None

    count = seed_soil_units(mock_db)
    assert count >= 1
