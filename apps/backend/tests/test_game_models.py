"""Unit tests for Chapter, Lesson, Mission, Progress, and Achievement models and repositories."""

import uuid
from unittest.mock import MagicMock

from app.modules.game.models import (
    Achievement,
    Chapter,
    Lesson,
    Mission,
    PlayerProgress,
    RegionContentStatus,
    UserAchievement,
)
from app.modules.game.repository import (
    AchievementRepository,
    ChapterRepository,
    LessonRepository,
    MissionRepository,
    PlayerProgressRepository,
    RegionContentStatusRepository,
)


def test_chapter_defaults() -> None:
    chapter = Chapter(
        chapter_number=1,
        title="O Ciclo da Terra",
        learning_objective="Compreender as estações do ano e os sinais do céu",
        is_common=True,
    )
    assert chapter.chapter_number == 1
    assert chapter.title == "O Ciclo da Terra"
    assert chapter.is_common is True
    assert chapter.provisional is True
    assert isinstance(chapter.id, uuid.UUID)
    assert "#1" in repr(chapter)


def test_lesson_defaults() -> None:
    chapter_id = uuid.uuid4()
    lesson = Lesson(
        chapter_id=chapter_id,
        topic="climate",
        title="Quando Chegam as Primeiras Chuvas",
        text_simple="A chuva boa molha a terra até ao fundo antes de semear.",
        audio_text="Escuta com atenção: antes de lançar a semente...",
        source="INAM / Guia Agrícola",
    )
    assert lesson.chapter_id == chapter_id
    assert lesson.region_id is None  # Common lesson
    assert lesson.topic == "climate"
    assert lesson.verified is False
    assert lesson.is_synthetic is False
    assert lesson.language == "pt"
    assert isinstance(lesson.id, uuid.UUID)
    assert "Quando Chegam" in repr(lesson)


def test_mission_defaults() -> None:
    chapter_id = uuid.uuid4()
    mission = Mission(
        chapter_id=chapter_id,
        mission_type="choose_date",
        title="O Momento Certo de Semear",
        prompt_simple="Olha para a terra e para os dados. Deves semear hoje ou esperar?",
        learning_note="Semear antes da terra acumular humidade suficiente queima a semente.",
        max_score=100,
    )
    assert mission.chapter_id == chapter_id
    assert mission.mission_type == "choose_date"
    assert mission.max_score == 100
    assert mission.verified is False
    assert isinstance(mission.id, uuid.UUID)
    assert "choose_date" in repr(mission)


def test_player_progress_defaults() -> None:
    user_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    mission_id = uuid.uuid4()

    progress = PlayerProgress(
        user_id=user_id,
        chapter_id=chapter_id,
        mission_id=mission_id,
        status="completed",
        score=90,
    )
    assert progress.user_id == user_id
    assert progress.mission_id == mission_id
    assert progress.status == "completed"
    assert progress.score == 90
    assert isinstance(progress.id, uuid.UUID)
    assert "completed" in repr(progress)


def test_achievement_defaults() -> None:
    achievement = Achievement(
        code="rain_watcher",
        title="Guardião das Chuvas",
        description="Completou o capítulo de leitura de chuva e humidade",
    )
    assert achievement.code == "rain_watcher"
    assert achievement.title == "Guardião das Chuvas"
    assert isinstance(achievement.id, uuid.UUID)
    assert "rain_watcher" in repr(achievement)


def test_user_achievement_defaults() -> None:
    user_id = uuid.uuid4()
    achievement_id = uuid.uuid4()
    user_ach = UserAchievement(user_id=user_id, achievement_id=achievement_id)
    assert user_ach.user_id == user_id
    assert user_ach.achievement_id == achievement_id
    assert isinstance(user_ach.id, uuid.UUID)


def test_region_content_status_defaults() -> None:
    region_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    status_obj = RegionContentStatus(
        region_id=region_id,
        chapter_id=chapter_id,
        lessons_total=3,
        lessons_verified=2,
        missions_total=2,
        status="review",
    )
    assert status_obj.region_id == region_id
    assert status_obj.chapter_id == chapter_id
    assert status_obj.status == "review"
    assert isinstance(status_obj.id, uuid.UUID)


def test_chapter_repository() -> None:
    mock_db = MagicMock()
    chapter = Chapter(
        chapter_number=1,
        title="Capítulo 1",
        learning_objective="Aprender o básico",
    )
    mock_db.scalars.return_value.all.return_value = [chapter]
    mock_db.scalars.return_value.first.return_value = chapter

    repo = ChapterRepository(mock_db)
    assert repo.list() == [chapter]
    assert repo.get_by_id(chapter.id) == chapter
    assert repo.get_by_number(1) == chapter

    created = repo.create(chapter)
    assert created == chapter
    mock_db.add.assert_called_once_with(chapter)


def test_lesson_repository() -> None:
    mock_db = MagicMock()
    chapter_id = uuid.uuid4()
    lesson = Lesson(
        chapter_id=chapter_id,
        topic="soil",
        title="Tipos de Solo",
        text_simple="A terra vermelha segura água.",
        audio_text="Ouve...",
        source="IIAM",
    )
    mock_db.scalars.return_value.first.return_value = lesson
    mock_db.scalars.return_value.all.return_value = [lesson]

    repo = LessonRepository(mock_db)
    assert repo.get_by_id(lesson.id) == lesson
    assert repo.list_by_chapter_and_region(chapter_id) == [lesson]
    assert repo.create(lesson) == lesson


def test_mission_repository() -> None:
    mock_db = MagicMock()
    chapter_id = uuid.uuid4()
    mission = Mission(
        chapter_id=chapter_id,
        mission_type="interpret_signal",
        title="Ver o Vigor da Machamba",
        prompt_simple="O verde está forte?",
        learning_note="O vigor mostra saúde da planta.",
    )
    mock_db.scalars.return_value.first.return_value = mission
    mock_db.scalars.return_value.all.return_value = [mission]

    repo = MissionRepository(mock_db)
    assert repo.get_by_id(mission.id) == mission
    assert repo.list_by_chapter_and_region(chapter_id) == [mission]
    assert repo.create(mission) == mission


def test_player_progress_repository() -> None:
    mock_db = MagicMock()
    user_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    mission_id = uuid.uuid4()

    progress = PlayerProgress(
        user_id=user_id,
        chapter_id=chapter_id,
        mission_id=mission_id,
        status="in_progress",
    )
    mock_db.scalars.return_value.first.return_value = progress
    mock_db.scalars.return_value.all.return_value = [progress]

    repo = PlayerProgressRepository(mock_db)
    assert repo.get_by_user_and_mission(user_id, mission_id) == progress
    assert repo.get_by_user_and_lesson(user_id, uuid.uuid4()) == progress
    assert repo.list_by_user(user_id) == [progress]
    assert repo.save(progress) == progress


def test_achievement_repository() -> None:
    mock_db = MagicMock()
    user_id = uuid.uuid4()
    achievement = Achievement(
        code="master_farmer",
        title="Mestre Agricultor",
        description="Terminou todos os capítulos",
    )
    mock_db.scalars.return_value.all.return_value = [achievement]
    mock_db.scalars.return_value.first.return_value = achievement

    repo = AchievementRepository(mock_db)
    assert repo.list() == [achievement]
    assert repo.get_by_code("master_farmer") == achievement
    assert repo.get_user_achievements(user_id) == [achievement]

    # Test unlock when already exists
    unlocked = repo.unlock_for_user(user_id, achievement.id)
    assert unlocked is not None

    # Test unlock when does not exist
    mock_db.scalars.return_value.first.return_value = None
    new_unlocked = repo.unlock_for_user(user_id, achievement.id)
    assert new_unlocked.user_id == user_id


def test_region_content_status_repository() -> None:
    mock_db = MagicMock()
    region_id = uuid.uuid4()
    chapter_id = uuid.uuid4()
    status_obj = RegionContentStatus(
        region_id=region_id,
        chapter_id=chapter_id,
        status="published",
    )
    mock_db.scalars.return_value.first.return_value = status_obj

    repo = RegionContentStatusRepository(mock_db)
    assert repo.get_status(region_id, chapter_id) == status_obj
    assert repo.save(status_obj) == status_obj
