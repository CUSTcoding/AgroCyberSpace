"""Unit tests for Region, District, and Community models and repositories."""

import uuid
from unittest.mock import MagicMock

from app.modules.regions.models import Community, District, Region
from app.modules.regions.repository import (
    CommunityRepository,
    DistrictRepository,
    RegionRepository,
)


def test_region_model_defaults() -> None:
    region = Region(
        code="gaza",
        name="Gaza",
        description="Chókwè e vale do Limpopo",
    )
    assert region.code == "gaza"
    assert region.name == "Gaza"
    assert region.is_proposed_study_area is True
    assert isinstance(region.id, uuid.UUID)
    assert "gaza" in repr(region)


def test_district_model_defaults() -> None:
    region_id = uuid.uuid4()
    district = District(
        region_id=region_id,
        code="chokwe",
        name="Chókwè",
        province="Gaza",
    )
    assert district.region_id == region_id
    assert district.code == "chokwe"
    assert district.name == "Chókwè"
    assert district.province == "Gaza"
    assert district.source == "CENACARTA 2017"
    assert isinstance(district.id, uuid.UUID)
    assert "chokwe" in repr(district)


def test_community_model_defaults() -> None:
    district_id = uuid.uuid4()
    community = Community(
        district_id=district_id,
        name="Lionde",
        description="Zona agrícola de regadio",
    )
    assert community.district_id == district_id
    assert community.name == "Lionde"
    assert community.description == "Zona agrícola de regadio"
    assert isinstance(community.id, uuid.UUID)
    assert "Lionde" in repr(community)


def test_region_repository() -> None:
    mock_db = MagicMock()
    region_id = uuid.uuid4()
    region = Region(id=region_id, code="zambezia", name="Zambézia")

    mock_db.scalars.return_value.first.return_value = region
    mock_db.scalars.return_value.all.return_value = [region]

    repo = RegionRepository(mock_db)

    # get_by_id
    assert repo.get_by_id(region_id) == region
    # get_by_code
    assert repo.get_by_code("zambezia") == region
    # list
    assert repo.list() == [region]

    # create
    created = repo.create(region)
    assert created == region
    mock_db.add.assert_called_once_with(region)
    mock_db.commit.assert_called_once()


def test_region_repository_get_geojson() -> None:
    mock_db = MagicMock()
    region_id = uuid.uuid4()

    mock_row = MagicMock()
    mock_row.id = region_id
    mock_row.code = "tete"
    mock_row.name = "Tete"
    mock_row.description = "Angónia e vale do Zambeze"
    mock_row.is_proposed_study_area = True
    mock_row.geojson = (
        '{"type": "Polygon", "coordinates": [[[33.0, -15.0], [34.0, -15.0], '
        "[34.0, -16.0], [33.0, -15.0]]]}"
    )

    mock_db.execute.return_value.first.return_value = mock_row

    repo = RegionRepository(mock_db)
    feature = repo.get_geojson(region_id)

    assert feature is not None
    assert feature["type"] == "Feature"
    assert feature["id"] == str(region_id)
    assert feature["properties"]["code"] == "tete"
    assert feature["geometry"]["type"] == "Polygon"


def test_district_repository() -> None:
    mock_db = MagicMock()
    region_id = uuid.uuid4()
    district_id = uuid.uuid4()
    district = District(
        id=district_id,
        region_id=region_id,
        code="mocuba",
        name="Mocuba",
        province="Zambézia",
    )

    mock_db.scalars.return_value.first.return_value = district
    mock_db.scalars.return_value.all.return_value = [district]

    repo = DistrictRepository(mock_db)

    assert repo.get_by_id(district_id) == district
    assert repo.get_by_code("mocuba") == district
    assert repo.list_by_region(region_id) == [district]

    created = repo.create(district)
    assert created == district


def test_community_repository() -> None:
    mock_db = MagicMock()
    district_id = uuid.uuid4()
    community = Community(
        district_id=district_id,
        name="Guijá Centro",
    )

    mock_db.scalars.return_value.first.return_value = community
    mock_db.scalars.return_value.all.return_value = [community]

    repo = CommunityRepository(mock_db)

    assert repo.get_by_id(community.id) == community
    assert repo.list_by_district(district_id) == [community]

    created = repo.create(community)
    assert created == community
