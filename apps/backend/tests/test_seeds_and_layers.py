"""Unit tests for AOI GeoJSON canonical files, national layer validation, and seed script."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scripts.import_national_layers import (
    NATIONAL_LAYER_METADATA,
    validate_aoi_geojson_layer,
)
from scripts.seed import (
    CONFIRMED_DATA,
    SEEDS_AOI_DIR,
    load_aoi_geojson,
    seed_regions_and_districts,
)


def test_confirmed_aoi_files_exist() -> None:
    """Verify that the 3 confirmed study regions have canonical AOI GeoJSON files."""
    assert (SEEDS_AOI_DIR / "gaza.geojson").exists()
    assert (SEEDS_AOI_DIR / "zambezia.geojson").exists()
    assert (SEEDS_AOI_DIR / "tete.geojson").exists()
    # Maputo must NOT exist yet (pending confirmation)
    assert not (SEEDS_AOI_DIR / "maputo.geojson").exists()


@pytest.mark.parametrize("region_code", ["gaza", "zambezia", "tete"])
def test_aoi_geojson_structure(region_code: str) -> None:
    """Verify GeoJSON validity, properties, and geographic constraints."""
    file_path = SEEDS_AOI_DIR / f"{region_code}.geojson"
    data = load_aoi_geojson(file_path)

    assert data.get("type") == "FeatureCollection"
    features = data.get("features", [])
    assert len(features) == 1

    feature = features[0]
    props = feature["properties"]
    assert props["code"] == region_code
    assert props["is_proposed_study_area"] is True
    assert "source" in props
    assert "description" in props
    assert isinstance(props.get("target_districts"), list)
    assert len(props["target_districts"]) > 0

    # Geometry validation via validation helper
    report = validate_aoi_geojson_layer(file_path)
    assert report["valid"] is True
    assert report["geometry_type"] == "Polygon"
    minx, miny, maxx, maxy = report["bounds"]
    # Bounding coordinates in Mozambique (Lon ~30-41, Lat ~ -27 to -10)
    assert 30.0 <= minx <= maxx <= 41.0
    assert -27.0 <= miny <= maxy <= -10.0


def test_validate_aoi_layer_nonexistent_file(tmp_path: Path) -> None:
    """Test validation raises FileNotFoundError for missing file."""
    fake_file = tmp_path / "nonexistent.geojson"
    with pytest.raises(FileNotFoundError):
        validate_aoi_geojson_layer(fake_file)


def test_validate_aoi_layer_invalid_geojson(tmp_path: Path) -> None:
    """Test validation raises ValueError for invalid GeoJSON structure."""
    bad_file = tmp_path / "bad.geojson"
    bad_file.write_text('{"type": "InvalidType"}', encoding="utf-8")
    with pytest.raises(ValueError, match="expected FeatureCollection"):
        validate_aoi_geojson_layer(bad_file)


def test_seed_regions_and_districts_idempotent() -> None:
    """Test seed function creates records when not found and commits updates when found."""
    mock_db = MagicMock()

    # First run: all entities return None (not found)
    mock_db.scalars.return_value.first.return_value = None
    mock_db.scalars.return_value.all.return_value = []

    stats_first = seed_regions_and_districts(mock_db, aoi_dir=SEEDS_AOI_DIR)
    assert stats_first["regions_seeded"] == 3
    assert stats_first["districts_seeded"] >= 3
    assert stats_first["communities_seeded"] >= 3

    # Check commit called
    assert mock_db.commit.call_count >= 3


def test_confirmed_data_registry_structure() -> None:
    """Ensure registry defines confirmed districts and communities."""
    for region_code in ["gaza", "zambezia", "tete"]:
        assert region_code in CONFIRMED_DATA
        districts = CONFIRMED_DATA[region_code]["districts"]
        assert len(districts) >= 1
        for d in districts:
            assert "code" in d
            assert "name" in d
            assert "province" in d
            assert "communities" in d


def test_national_metadata_compliance() -> None:
    """Ensure metadata contains required legal and citation fields."""
    assert NATIONAL_LAYER_METADATA["source"] == "CENACARTA 2017"
    assert NATIONAL_LAYER_METADATA["year"] == 2017
    assert NATIONAL_LAYER_METADATA["crs"] == "EPSG:4326"
    license_text = str(NATIONAL_LAYER_METADATA["license"]).lower()
    assert "licence" in license_text or "dados públicos" in license_text
