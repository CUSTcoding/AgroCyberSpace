"""Repository layer for Chapter, Lesson, Mission, PlayerProgress, and Achievements."""

from __future__ import annotations

import builtins
import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.game.models import (
    Achievement,
    Chapter,
    Lesson,
    Mission,
    PlayerProgress,
    RegionContentStatus,
    UserAchievement,
)


class ChapterRepository:
    """Repository for educational game chapters."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[Chapter]:
        """List all 12 chapters ordered by sequence."""
        stmt = select(Chapter).order_by(Chapter.order.asc(), Chapter.chapter_number.asc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, chapter_id: uuid.UUID) -> Chapter | None:
        """Find chapter by unique UUID."""
        stmt = select(Chapter).where(Chapter.id == chapter_id)
        return self.db.scalars(stmt).first()

    def get_by_number(self, chapter_number: int) -> Chapter | None:
        """Find chapter by chapter number (1 to 12)."""
        stmt = select(Chapter).where(Chapter.chapter_number == chapter_number)
        return self.db.scalars(stmt).first()

    def create(self, chapter: Chapter) -> Chapter:
        """Persist a chapter."""
        self.db.add(chapter)
        self.db.commit()
        self.db.refresh(chapter)
        return chapter


class LessonRepository:
    """Repository for chapter lessons."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, lesson_id: uuid.UUID) -> Lesson | None:
        """Find lesson by unique UUID."""
        stmt = select(Lesson).where(Lesson.id == lesson_id)
        return self.db.scalars(stmt).first()

    def list_by_chapter_and_region(
        self, chapter_id: uuid.UUID, region_id: uuid.UUID | None = None
    ) -> list[Lesson]:
        """List lessons for a chapter filtered by region or common lessons."""
        if region_id is not None:
            stmt = (
                select(Lesson)
                .where(
                    Lesson.chapter_id == chapter_id,
                    or_(Lesson.region_id == region_id, Lesson.region_id.is_(None)),
                )
                .order_by(Lesson.position.asc())
            )
        else:
            stmt = (
                select(Lesson)
                .where(Lesson.chapter_id == chapter_id)
                .order_by(Lesson.position.asc())
            )
        return list(self.db.scalars(stmt).all())

    def create(self, lesson: Lesson) -> Lesson:
        """Persist a lesson."""
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson


class MissionRepository:
    """Repository for chapter missions (desafios)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, mission_id: uuid.UUID) -> Mission | None:
        """Find mission by unique UUID."""
        stmt = select(Mission).where(Mission.id == mission_id)
        return self.db.scalars(stmt).first()

    def list_by_chapter_and_region(
        self, chapter_id: uuid.UUID, region_id: uuid.UUID | None = None
    ) -> list[Mission]:
        """List missions for a chapter filtered by region or common missions."""
        if region_id is not None:
            stmt = (
                select(Mission)
                .where(
                    Mission.chapter_id == chapter_id,
                    or_(Mission.region_id == region_id, Mission.region_id.is_(None)),
                )
                .order_by(Mission.position.asc())
            )
        else:
            stmt = (
                select(Mission)
                .where(Mission.chapter_id == chapter_id)
                .order_by(Mission.position.asc())
            )
        return list(self.db.scalars(stmt).all())

    def create(self, mission: Mission) -> Mission:
        """Persist a mission."""
        self.db.add(mission)
        self.db.commit()
        self.db.refresh(mission)
        return mission


class PlayerProgressRepository:
    """Repository for player progress on lessons and missions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_and_mission(
        self, user_id: uuid.UUID, mission_id: uuid.UUID
    ) -> PlayerProgress | None:
        """Find progress record for a user on a specific mission."""
        stmt = select(PlayerProgress).where(
            PlayerProgress.user_id == user_id,
            PlayerProgress.mission_id == mission_id,
        )
        return self.db.scalars(stmt).first()

    def get_by_user_and_lesson(
        self, user_id: uuid.UUID, lesson_id: uuid.UUID
    ) -> PlayerProgress | None:
        """Find progress record for a user on a specific lesson."""
        stmt = select(PlayerProgress).where(
            PlayerProgress.user_id == user_id,
            PlayerProgress.lesson_id == lesson_id,
        )
        return self.db.scalars(stmt).first()

    def list_by_user(self, user_id: uuid.UUID) -> list[PlayerProgress]:
        """List all progress records for a given user."""
        stmt = (
            select(PlayerProgress)
            .where(PlayerProgress.user_id == user_id)
            .order_by(PlayerProgress.updated_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def save(self, progress: PlayerProgress) -> PlayerProgress:
        """Persist or update a progress record."""
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress


class AchievementRepository:
    """Repository for achievements and player badges."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list(self) -> builtins.list[Achievement]:
        """List all available game achievements."""
        stmt = select(Achievement).order_by(Achievement.title.asc())
        return list(self.db.scalars(stmt).all())

    def get_by_code(self, code: str) -> Achievement | None:
        """Find achievement by code."""
        stmt = select(Achievement).where(func.lower(Achievement.code) == func.lower(code.strip()))
        return self.db.scalars(stmt).first()

    def create(self, achievement: Achievement) -> Achievement:
        """Persist an achievement."""
        self.db.add(achievement)
        self.db.commit()
        self.db.refresh(achievement)
        return achievement

    def get_user_achievements(self, user_id: uuid.UUID) -> builtins.list[Achievement]:
        """Retrieve all achievements unlocked by a specific user."""
        stmt = (
            select(Achievement)
            .join(UserAchievement, Achievement.id == UserAchievement.achievement_id)
            .where(UserAchievement.user_id == user_id)
            .order_by(UserAchievement.unlocked_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def unlock_for_user(self, user_id: uuid.UUID, achievement_id: uuid.UUID) -> UserAchievement:
        """Grant an achievement to a user if not already unlocked."""
        stmt = select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id,
        )
        existing = self.db.scalars(stmt).first()
        if existing is not None:
            return existing

        user_ach = UserAchievement(user_id=user_id, achievement_id=achievement_id)
        self.db.add(user_ach)
        self.db.commit()
        self.db.refresh(user_ach)
        return user_ach


class RegionContentStatusRepository:
    """Repository for regional content review and publication status."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_status(self, region_id: uuid.UUID, chapter_id: uuid.UUID) -> RegionContentStatus | None:
        """Get content status for a specific region and chapter."""
        stmt = select(RegionContentStatus).where(
            RegionContentStatus.region_id == region_id,
            RegionContentStatus.chapter_id == chapter_id,
        )
        return self.db.scalars(stmt).first()

    def save(self, status_obj: RegionContentStatus) -> RegionContentStatus:
        """Persist or update region content status."""
        self.db.add(status_obj)
        self.db.commit()
        self.db.refresh(status_obj)
        return status_obj
