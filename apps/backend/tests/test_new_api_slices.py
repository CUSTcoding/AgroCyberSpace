"""Tests for map configuration, content manifests, and template AI routes."""

import uuid
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.main import app
from app.modules.ai.schemas import ExplainRequest
from app.modules.ai.service import TemplateProvider
from app.modules.game.models import Lesson, Mission
from app.modules.game.service import GameService
from app.modules.regions.router import get_region_service
from app.modules.regions.service import RegionService


def test_template_provider_includes_provenance_and_limitations() -> None:
    request = ExplainRequest.model_validate(
        {
            "language": "pt",
            "context": {
                "category": "observed",
                "source": "NASA POWER",
                "dataset_version": "daily-v1",
                "limitations": ["Resolução regional"],
            },
        }
    )

    response = TemplateProvider().explain(request)

    assert response.technical_details["source"] == "NASA POWER"
    assert response.technical_details["dataset_version"] == "daily-v1"
    assert "Resolução regional" in response.limitations
    assert "não garantem produtividade" in response.limitations[-1]


def test_template_hint_marks_local_challenge_as_simulation() -> None:
    request = ExplainRequest.model_validate(
        {
            "language": "pt",
            "context": {
                "category": "simulation",
                "source": "AgroSpace local educational content",
                "dataset_version": "not-applicable",
                "limitations": ["No live environmental data is used."],
            },
        }
    )

    response = TemplateProvider().hint(request)

    assert "exemplo educativo" in response.message_simple
    assert "Nenhum dado real de satélite" in response.limitations[-1]


def test_explanation_context_rejects_personal_fields() -> None:
    with pytest.raises(ValidationError):
        ExplainRequest.model_validate(
            {
                "context": {
                    "category": "observed",
                    "source": "NASA POWER",
                    "dataset_version": "daily-v1",
                    "email": "player@example.test",
                }
            }
        )


@pytest.mark.anyio
async def test_ai_health_endpoint_uses_local_template_provider() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ai/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "provider": "template",
        "external_service": False,
    }


@pytest.mark.anyio
async def test_ai_explain_endpoint_returns_simple_explanation() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/ai/explain",
            json={
                "language": "pt",
                "context": {
                    "category": "observed",
                    "source": "NASA POWER",
                    "dataset_version": "daily-v1",
                    "limitations": ["Resolução regional"],
                },
            },
        )

    assert response.status_code == 200
    assert response.json()["technical_details"]["source"] == "NASA POWER"
    assert "Resolução regional" in response.json()["limitations"]


def test_manifest_excludes_unverified_and_unpublished_regional_content() -> None:
    service = GameService(MagicMock())
    region_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    verified_regional = Lesson(
        chapter_id=chapter_id,
        region_id=region_id,
        topic="climate",
        title="Verified",
        text_simple="Text",
        audio_text="Audio",
        source="Source",
        verified=True,
    )
    verified_common_mission = Mission(
        chapter_id=uuid.uuid4(),
        mission_type="interpret_signal",
        title="Common",
        prompt_simple="Prompt",
        learning_note="Note",
        verified=True,
    )
    service.lesson_repo = MagicMock()
    service.mission_repo = MagicMock()
    service.content_status_repo = MagicMock()
    service.lesson_repo.list_verified_for_manifest.return_value = [verified_regional]
    service.mission_repo.list_verified_for_manifest.return_value = [verified_common_mission]
    service.content_status_repo.list_published_chapter_ids.return_value = set()

    items = service.get_content_manifest(language="pt", region_id=region_id)

    assert [item.content_type for item in items] == ["mission"]
    assert items[0].id == verified_common_mission.id


@pytest.mark.anyio
async def test_map_config_endpoint_returns_bounds_without_layers() -> None:
    region_id = uuid.uuid4()
    service = MagicMock(spec=RegionService)
    service.get_map_config.return_value = {
        "region_id": str(region_id),
        "region_code": "gaza",
        "region_name": "Gaza",
        "bbox": [32.0, -25.0, 34.0, -23.0],
        "min_zoom": 5,
        "max_zoom": 12,
        "layers": [],
        "is_proposed_study_area": True,
        "data_as_of": "2026-11-15T00:00:00Z",
    }
    app.dependency_overrides[get_region_service] = lambda: service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/regions/{region_id}/map-config")
    finally:
        app.dependency_overrides.pop(get_region_service, None)

    assert response.status_code == 200
    assert response.json()["layers"] == []
    assert response.json()["bbox"] == [32.0, -25.0, 34.0, -23.0]


@pytest.mark.anyio
async def test_region_indicators_are_labeled_district_level() -> None:
    region_id = uuid.uuid4()
    service = MagicMock(spec=RegionService)
    service.list_region_indicators.return_value = (
        [
            {
                "district_id": uuid.uuid4(),
                "district_name": "Chókwè",
                "crop": "milho",
                "area_ha": 125.0,
                "production_t": 70.0,
                "campaign": "2023/2024",
                "year": 2023,
                "source": "INE/MADER",
            }
        ],
        1,
    )
    app.dependency_overrides[get_region_service] = lambda: service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/regions/{region_id}/indicators")
    finally:
        app.dependency_overrides.pop(get_region_service, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["items"][0]["spatial_level"] == "district"
    assert payload["items"][0]["indicator_type"] == "district_crop_stat"
    assert payload["items"][0]["source"] == "INE/MADER"
