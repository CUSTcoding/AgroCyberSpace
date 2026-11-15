"""Tests for authenticated game progression rules."""

import uuid
from typing import Any
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.modules.auth.dependencies import get_current_user
from app.modules.game.models import Achievement, Chapter, Lesson, Mission, PlayerProgress
from app.modules.game.router import get_game_service
from app.modules.game.service import GameService
from app.modules.users.models import User
from app.shared.exceptions import ConflictException, ValidationException


def make_service() -> Any:
    service = GameService(MagicMock())
    service.chapter_repo = MagicMock()
    service.lesson_repo = MagicMock()
    service.mission_repo = MagicMock()
    service.progress_repo = MagicMock()
    service.achievement_repo = MagicMock()
    service.progress_repo.save.side_effect = lambda progress: progress
    return service


def test_complete_lesson_is_idempotent() -> None:
    service = make_service()
    user_id = uuid.uuid4()
    lesson = Lesson(
        chapter_id=uuid.uuid4(),
        topic="soil",
        title="Lesson",
        text_simple="Text",
        audio_text="Audio",
        source="Source",
    )
    service.lesson_repo.get_by_id.return_value = lesson
    existing = PlayerProgress(
        user_id=user_id,
        chapter_id=lesson.chapter_id,
        lesson_id=lesson.id,
        status="completed",
    )
    service.progress_repo.get_by_user_and_lesson.return_value = existing

    result = service.complete_lesson(user_id, lesson.id)

    assert result is existing
    service.progress_repo.save.assert_not_called()


def test_start_mission_creates_progress_and_is_idempotent() -> None:
    service = make_service()
    user_id = uuid.uuid4()
    mission = Mission(
        chapter_id=uuid.uuid4(),
        mission_type="water_decision",
        title="Mission",
        prompt_simple="Choose",
        learning_note="Learn",
    )
    service.mission_repo.get_by_id.return_value = mission
    service.progress_repo.get_by_user_and_mission.return_value = None

    progress = service.start_mission(user_id, mission.id)

    assert progress.status == "in_progress"
    assert progress.started_at is not None
    service.progress_repo.save.assert_called_once_with(progress)

    service.progress_repo.get_by_user_and_mission.return_value = progress
    assert service.start_mission(user_id, mission.id) is progress
    assert service.progress_repo.save.call_count == 1


def test_submit_scores_only_authored_choices() -> None:
    service = make_service()
    user_id = uuid.uuid4()
    mission = Mission(
        chapter_id=uuid.uuid4(),
        mission_type="water_decision",
        title="Mission",
        prompt_simple="Choose",
        learning_note="Learn",
        answer_rules={
            "recommended_choice": "wait",
            "score_breakdown": {"wait": 100, "plant": 40},
        },
    )
    progress = PlayerProgress(
        user_id=user_id,
        chapter_id=mission.chapter_id,
        mission_id=mission.id,
        status="in_progress",
    )
    service.mission_repo.get_by_id.return_value = mission
    service.progress_repo.get_by_user_and_mission.return_value = progress

    result, submitted_mission, is_recommended = service.submit_mission(
        user_id,
        mission.id,
        {"choice": "wait"},
    )

    assert submitted_mission is mission
    assert result.status == "completed"
    assert result.score == 100
    assert result.attempts == 1
    assert result.submission_data == {"choice": "wait"}
    assert result.completed_at is not None
    assert is_recommended is True


def test_field_observation_is_preserved_when_mission_is_submitted() -> None:
    service = make_service()
    user_id = uuid.uuid4()
    mission = Mission(
        chapter_id=uuid.uuid4(),
        mission_type="field_observation_check",
        title="Mission",
        prompt_simple="Observe",
        learning_note="Compare what you see.",
        answer_rules={
            "recommended_choice": "wait",
            "score_breakdown": {"wait": 100},
        },
    )
    progress = PlayerProgress(
        user_id=user_id,
        chapter_id=mission.chapter_id,
        mission_id=mission.id,
        status="in_progress",
        submission_data={
            "field_observation": {"observed_condition": "soil is dry"},
        },
    )
    service.mission_repo.get_by_id.return_value = mission
    service.progress_repo.get_by_user_and_mission.return_value = progress

    service.submit_mission(user_id, mission.id, {"choice": "wait"})

    assert progress.submission_data == {
        "field_observation": {"observed_condition": "soil is dry"},
        "choice": "wait",
    }


@pytest.mark.parametrize(
    ("status", "submission", "error_type"),
    [
        (None, {"choice": "wait"}, ConflictException),
        ("completed", {"choice": "wait"}, ConflictException),
        ("in_progress", {"choice": "unknown"}, ValidationException),
    ],
)
def test_submit_rejects_invalid_mission_state_or_choice(
    status: str | None,
    submission: dict[str, str],
    error_type: type[Exception],
) -> None:
    service = make_service()
    user_id = uuid.uuid4()
    mission = Mission(
        chapter_id=uuid.uuid4(),
        mission_type="water_decision",
        title="Mission",
        prompt_simple="Choose",
        learning_note="Learn",
        answer_rules={"score_breakdown": {"wait": 100}},
    )
    service.mission_repo.get_by_id.return_value = mission
    service.progress_repo.get_by_user_and_mission.return_value = (
        PlayerProgress(
            user_id=user_id,
            chapter_id=mission.chapter_id,
            mission_id=mission.id,
            status=status,
        )
        if status is not None
        else None
    )

    with pytest.raises(error_type):
        service.submit_mission(user_id, mission.id, submission)


def test_completed_mission_cannot_be_started_again() -> None:
    service = make_service()
    user_id = uuid.uuid4()
    mission = Mission(
        chapter_id=uuid.uuid4(),
        mission_type="water_decision",
        title="Mission",
        prompt_simple="Choose",
        learning_note="Learn",
    )
    service.mission_repo.get_by_id.return_value = mission
    service.progress_repo.get_by_user_and_mission.return_value = PlayerProgress(
        user_id=user_id,
        chapter_id=mission.chapter_id,
        mission_id=mission.id,
        status="completed",
    )

    with pytest.raises(ConflictException):
        service.start_mission(user_id, mission.id)


def test_list_progress_returns_page_and_total() -> None:
    service = make_service()
    user_id = uuid.uuid4()
    item = PlayerProgress(
        user_id=user_id,
        chapter_id=uuid.uuid4(),
        status="completed",
    )
    service.progress_repo.list_page_by_user.return_value = [item]
    service.progress_repo.count_by_user.return_value = 4

    items, total = service.list_progress(user_id, limit=1, offset=2)

    assert items == [item]
    assert total == 4
    service.progress_repo.list_page_by_user.assert_called_once_with(user_id, 1, 2)


def test_list_achievements_marks_only_owned_badges_unlocked() -> None:
    service = make_service()
    user_id = uuid.uuid4()
    unlocked = Achievement(code="first", title="First", description="Completed one task")
    locked = Achievement(code="next", title="Next", description="Completed more tasks")
    service.achievement_repo.list.return_value = [unlocked, locked]
    service.achievement_repo.get_user_achievements.return_value = [unlocked]

    items = service.list_achievements(user_id)

    assert [item.unlocked for item in items] == [True, False]


def test_next_chapter_unlocks_only_after_all_prior_content_is_completed() -> None:
    service = make_service()
    user_id = uuid.uuid4()
    first_chapter = Chapter(
        chapter_number=1,
        title="First",
        learning_objective="Learn first",
    )
    second_chapter = Chapter(
        chapter_number=2,
        title="Second",
        learning_objective="Learn next",
    )
    lesson = Lesson(
        chapter_id=first_chapter.id,
        topic="soil",
        title="Lesson",
        text_simple="Text",
        audio_text="Audio",
        source="Source",
    )
    mission = Mission(
        chapter_id=first_chapter.id,
        mission_type="interpret_signal",
        title="Mission",
        prompt_simple="Choose",
        learning_note="Learn",
    )
    service.chapter_repo.list.return_value = [first_chapter, second_chapter]
    service.chapter_repo.get_by_number.side_effect = [first_chapter]
    service.lesson_repo.list_by_chapter_and_region.return_value = [lesson]
    service.mission_repo.list_by_chapter_and_region.return_value = [mission]
    service.progress_repo.list_by_user.return_value = [
        PlayerProgress(
            user_id=user_id,
            chapter_id=first_chapter.id,
            lesson_id=lesson.id,
            status="completed",
        )
    ]

    summaries = service.list_chapters(user_id=user_id)

    assert summaries[0].is_unlocked is True
    assert summaries[1].is_unlocked is False

    service.chapter_repo.get_by_number.side_effect = [first_chapter]
    service.progress_repo.list_by_user.return_value.append(
        PlayerProgress(
            user_id=user_id,
            chapter_id=first_chapter.id,
            mission_id=mission.id,
            status="completed",
        )
    )
    summaries = service.list_chapters(user_id=user_id)

    assert summaries[1].is_unlocked is True


@pytest.mark.anyio
async def test_mission_start_requires_authentication() -> None:
    app.dependency_overrides[get_db] = lambda: MagicMock()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(f"/api/v1/game/missions/{uuid.uuid4()}/start")

        assert response.status_code == 401
        assert response.json()["error"]["code"] == "UNAUTHORIZED"
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.anyio
async def test_lesson_completion_returns_authenticated_player_progress() -> None:
    user = User(email="player@example.test", hashed_password="hash", full_name="Player")
    progress = PlayerProgress(
        user_id=user.id,
        chapter_id=uuid.uuid4(),
        lesson_id=uuid.uuid4(),
        status="completed",
        attempts=1,
    )
    service = MagicMock()
    service.complete_lesson.return_value = progress
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_game_service] = lambda: service
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(f"/api/v1/game/lessons/{progress.lesson_id}/complete")

        assert response.status_code == 200
        assert response.json()["status"] == "completed"
        assert "user_id" not in response.json()
        service.complete_lesson.assert_called_once_with(user.id, progress.lesson_id)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_game_service, None)
