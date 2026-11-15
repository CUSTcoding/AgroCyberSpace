"""Integration tests for game chapters, lessons, and missions endpoints."""

import uuid
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.game.models import Chapter, Lesson, Mission
from app.modules.game.router import get_game_service
from app.modules.game.schemas import ChapterDetail, ChapterSummary, LessonRead, MissionRead
from app.modules.game.service import GameService
from app.modules.users.models import User


@pytest.fixture
def mock_game_db() -> tuple[MagicMock, Chapter, Lesson, Mission]:
    """Provide mock database with Chapter, Lesson, and Mission."""
    mock_db = MagicMock()
    chapter_id = uuid.uuid4()
    lesson_id = uuid.uuid4()
    mission_id = uuid.uuid4()

    chapter = Chapter(
        id=chapter_id,
        chapter_number=1,
        title="O Olhar do Céu",
        learning_objective="Compreender os sinais da terra e satélites",
        is_common=True,
    )
    lesson = Lesson(
        id=lesson_id,
        chapter_id=chapter_id,
        topic="satellite_basics",
        title="O Que Vê o Satélite",
        text_simple="O satélite olha de longe para ver onde a vegetação está forte.",
        audio_text="O satélite observa...",
        source="NASA / IIAM",
    )
    mission = Mission(
        id=mission_id,
        chapter_id=chapter_id,
        mission_type="interpret_signal",
        title="Interpretar o Sinal",
        prompt_simple="Observa as três machambas. Qual parece mais vigorosa?",
        learning_note="O sinal verde mais forte indica biomassa mais densa.",
        configuration={"sample": "data"},
        answer_rules={"secret_key": "Option A"},  # Should not be leaked in response
    )

    return mock_db, chapter, lesson, mission


@pytest.mark.anyio
async def test_list_chapters_endpoint(
    mock_game_db: tuple[MagicMock, Chapter, Lesson, Mission],
) -> None:
    """Test GET /api/v1/game/chapters."""
    mock_db, chapter, _, _ = mock_game_db
    mock_db.scalars.return_value.all.return_value = [chapter]
    mock_db.scalars.return_value.first.return_value = chapter
    service = MagicMock(spec=GameService)
    service.list_chapters.return_value = [
        ChapterSummary.model_validate(chapter).model_copy(update={"is_unlocked": True})
    ]

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: User(
        email="player@example.test",
        hashed_password="hash",
        full_name="Player",
    )
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/game/chapters")
            assert resp.status_code == 200
            data = resp.json()
            assert "items" in data
            assert data["total"] == 1
            assert data["items"][0]["title"] == "O Olhar do Céu"
            assert data["items"][0]["is_unlocked"] is True
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_game_service, None)
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.anyio
async def test_get_chapter_detail_endpoint(
    mock_game_db: tuple[MagicMock, Chapter, Lesson, Mission],
) -> None:
    """Test GET /api/v1/game/chapters/{id}."""
    mock_db, chapter, lesson, mission = mock_game_db
    mock_db.scalars.return_value.first.return_value = chapter
    mock_db.scalars.return_value.all.side_effect = [[lesson], [mission]]
    service = MagicMock(spec=GameService)
    service.get_chapter.return_value = ChapterDetail(
        id=chapter.id,
        chapter_number=chapter.chapter_number,
        title=chapter.title,
        learning_objective=chapter.learning_objective,
        is_common=chapter.is_common,
        topics=chapter.topics,
        order=chapter.order,
        provisional=chapter.provisional,
        is_unlocked=True,
        lessons=[LessonRead.model_validate(lesson)],
        missions=[MissionRead.model_validate(mission)],
    )

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: User(
        email="player@example.test",
        hashed_password="hash",
        full_name="Player",
    )
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/game/chapters/{chapter.id}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["id"] == str(chapter.id)
            assert data["title"] == "O Olhar do Céu"
            assert len(data["lessons"]) == 1
            assert data["lessons"][0]["title"] == "O Que Vê o Satélite"
            assert len(data["missions"]) == 1
            assert data["missions"][0]["mission_type"] == "interpret_signal"
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_game_service, None)
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.anyio
async def test_get_chapter_not_found_endpoint(
    mock_game_db: tuple[MagicMock, Chapter, Lesson, Mission],
) -> None:
    """Test GET /api/v1/game/chapters/{id} when not found."""
    mock_db, _, _, _ = mock_game_db
    mock_db.scalars.return_value.first.return_value = None
    service = MagicMock(spec=GameService)
    service.get_chapter.side_effect = GameService(mock_db).get_chapter

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_game_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: User(
        email="player@example.test",
        hashed_password="hash",
        full_name="Player",
    )
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            fake_id = uuid.uuid4()
            resp = await client.get(f"/api/v1/game/chapters/{fake_id}")
            assert resp.status_code == 404
            data = resp.json()
            assert "error" in data
            assert data["error"]["code"] == "NOT_FOUND"
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_game_service, None)
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.anyio
async def test_get_lesson_endpoint(
    mock_game_db: tuple[MagicMock, Chapter, Lesson, Mission],
) -> None:
    """Test GET /api/v1/game/lessons/{id}."""
    mock_db, _, lesson, _ = mock_game_db
    mock_db.scalars.return_value.first.return_value = lesson

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/game/lessons/{lesson.id}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["id"] == str(lesson.id)
            assert data["title"] == "O Que Vê o Satélite"
            assert data["source"] == "NASA / IIAM"
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
async def test_list_missions_endpoint(
    mock_game_db: tuple[MagicMock, Chapter, Lesson, Mission],
) -> None:
    """Test GET /api/v1/game/missions."""
    mock_db, chapter, _, mission = mock_game_db
    mock_db.scalars.return_value.all.return_value = [mission]

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/game/missions?chapter_id={chapter.id}")
            assert resp.status_code == 200
            data = resp.json()
            assert "items" in data
            assert data["total"] == 1
            assert data["items"][0]["title"] == "Interpretar o Sinal"
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
async def test_get_mission_detail_endpoint_omits_answers(
    mock_game_db: tuple[MagicMock, Chapter, Lesson, Mission],
) -> None:
    """Test GET /api/v1/game/missions/{id} returns details but omits answer_rules."""
    mock_db, _, _, mission = mock_game_db
    mock_db.scalars.return_value.first.return_value = mission

    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get(f"/api/v1/game/missions/{mission.id}")
            assert resp.status_code == 200
            data = resp.json()
            assert data["id"] == str(mission.id)
            assert data["mission_type"] == "interpret_signal"
            assert "configuration" in data
            # Crucial: answer_rules must NOT be exposed to client
            assert "answer_rules" not in data
            assert "secret_key" not in str(data)
    finally:
        app.dependency_overrides.pop(get_db, None)
