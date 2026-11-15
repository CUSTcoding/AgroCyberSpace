"""Domain service layer for game chapters, lessons, and missions."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.modules.game.models import Lesson, Mission, PlayerProgress
from app.modules.game.repository import (
    AchievementRepository,
    ChapterRepository,
    LessonRepository,
    MissionRepository,
    PlayerProgressRepository,
    RegionContentStatusRepository,
)
from app.modules.game.schemas import (
    AchievementRead,
    ChapterDetail,
    ChapterSummary,
    ContentManifestItem,
    LessonRead,
    MissionRead,
)
from app.shared.exceptions import ConflictException, NotFoundException, ValidationException


class GameService:
    """Orchestrates game content, unlocking rules, and chapter progression."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.chapter_repo = ChapterRepository(db)
        self.lesson_repo = LessonRepository(db)
        self.mission_repo = MissionRepository(db)
        self.progress_repo = PlayerProgressRepository(db)
        self.achievement_repo = AchievementRepository(db)
        self.content_status_repo = RegionContentStatusRepository(db)

    def list_chapters(
        self,
        user_id: uuid.UUID | None = None,
        region_id: uuid.UUID | None = None,
    ) -> list[ChapterSummary]:
        """List all 12 chapters with computed unlock status."""
        chapters = self.chapter_repo.list()

        completed_lesson_ids: set[uuid.UUID] = set()
        completed_mission_ids: set[uuid.UUID] = set()
        if user_id is not None:
            user_progress = self.progress_repo.list_by_user(user_id)
            for prog in user_progress:
                if prog.status == "completed":
                    if prog.lesson_id is not None:
                        completed_lesson_ids.add(prog.lesson_id)
                    if prog.mission_id is not None:
                        completed_mission_ids.add(prog.mission_id)

        summaries: list[ChapterSummary] = []
        for ch in chapters:
            is_unlocked = True
            unlock_rule = ch.unlock_rule or {}
            req_chapters = unlock_rule.get("requires_completed_chapters", [])
            if req_chapters:
                is_unlocked = user_id is not None and all(
                    self._is_chapter_completed(
                        chapter_number=req,
                        completed_lesson_ids=completed_lesson_ids,
                        completed_mission_ids=completed_mission_ids,
                        region_id=region_id,
                    )
                    for req in req_chapters
                )
            elif ch.chapter_number > 1:
                is_unlocked = user_id is not None and self._is_chapter_completed(
                    chapter_number=ch.chapter_number - 1,
                    completed_lesson_ids=completed_lesson_ids,
                    completed_mission_ids=completed_mission_ids,
                    region_id=region_id,
                )

            summary = ChapterSummary(
                id=ch.id,
                chapter_number=ch.chapter_number,
                title=ch.title,
                learning_objective=ch.learning_objective,
                is_common=ch.is_common,
                topics=ch.topics,
                order=ch.order,
                provisional=ch.provisional,
                is_unlocked=is_unlocked,
            )
            summaries.append(summary)

        return summaries

    def _is_chapter_completed(
        self,
        chapter_number: int,
        completed_lesson_ids: set[uuid.UUID],
        completed_mission_ids: set[uuid.UUID],
        region_id: uuid.UUID | None,
    ) -> bool:
        """Require all lessons and missions for a chapter to be completed."""
        chapter = self.chapter_repo.get_by_number(chapter_number)
        if chapter is None:
            return False
        lessons = self.lesson_repo.list_by_chapter_and_region(chapter.id, region_id)
        missions = self.mission_repo.list_by_chapter_and_region(chapter.id, region_id)
        required_lessons = {lesson.id for lesson in lessons}
        required_missions = {mission.id for mission in missions}
        if not required_lessons and not required_missions:
            return False
        return required_lessons <= completed_lesson_ids and required_missions <= (
            completed_mission_ids
        )

    def get_chapter(
        self,
        chapter_id: uuid.UUID,
        user_id: uuid.UUID,
        region_id: uuid.UUID | None = None,
    ) -> ChapterDetail:
        """Get chapter details with region-specific or common lessons and missions."""
        chapter = self.chapter_repo.get_by_id(chapter_id)
        if chapter is None:
            raise NotFoundException(
                message=f"Chapter with id '{chapter_id}' was not found.",
                details={"chapter_id": str(chapter_id)},
            )

        lessons = self.lesson_repo.list_by_chapter_and_region(chapter_id, region_id=region_id)
        missions = self.mission_repo.list_by_chapter_and_region(chapter_id, region_id=region_id)

        return ChapterDetail(
            id=chapter.id,
            chapter_number=chapter.chapter_number,
            title=chapter.title,
            learning_objective=chapter.learning_objective,
            is_common=chapter.is_common,
            topics=chapter.topics,
            order=chapter.order,
            provisional=chapter.provisional,
            is_unlocked=next(
                summary.is_unlocked
                for summary in self.list_chapters(user_id=user_id)
                if summary.id == chapter.id
            ),
            lessons=[LessonRead.model_validate(les) for les in lessons],
            missions=[MissionRead.model_validate(m) for m in missions],
        )

    def get_lesson(self, lesson_id: uuid.UUID) -> Lesson:
        """Fetch a specific lesson by UUID."""
        lesson = self.lesson_repo.get_by_id(lesson_id)
        if lesson is None:
            raise NotFoundException(
                message=f"Lesson with id '{lesson_id}' was not found.",
                details={"lesson_id": str(lesson_id)},
            )
        return lesson

    def list_missions(
        self,
        chapter_id: uuid.UUID | None = None,
        region_id: uuid.UUID | None = None,
    ) -> list[Mission]:
        """List missions with optional chapter and region filters."""
        if chapter_id is not None:
            return self.mission_repo.list_by_chapter_and_region(chapter_id, region_id=region_id)
        # If no chapter filter, list for all chapters
        all_chapters = self.chapter_repo.list()
        result: list[Mission] = []
        for ch in all_chapters:
            result.extend(self.mission_repo.list_by_chapter_and_region(ch.id, region_id=region_id))
        return result

    def get_mission(self, mission_id: uuid.UUID) -> Mission:
        """Fetch a specific mission by UUID."""
        mission = self.mission_repo.get_by_id(mission_id)
        if mission is None:
            raise NotFoundException(
                message=f"Mission with id '{mission_id}' was not found.",
                details={"mission_id": str(mission_id)},
            )
        return mission

    def complete_lesson(self, user_id: uuid.UUID, lesson_id: uuid.UUID) -> PlayerProgress:
        """Mark a lesson complete for a player; repeated completion is idempotent."""
        lesson = self.get_lesson(lesson_id)
        progress = self.progress_repo.get_by_user_and_lesson(user_id, lesson_id)
        if progress is not None and progress.status == "completed":
            return progress

        now = datetime.now(UTC)
        if progress is None:
            progress = PlayerProgress(
                user_id=user_id,
                chapter_id=lesson.chapter_id,
                lesson_id=lesson_id,
                status="completed",
                attempts=1,
                started_at=now,
                completed_at=now,
            )
        else:
            progress.status = "completed"
            progress.attempts += 1
            progress.completed_at = now
            progress.started_at = progress.started_at or now
        return self.progress_repo.save(progress)

    def start_mission(self, user_id: uuid.UUID, mission_id: uuid.UUID) -> PlayerProgress:
        """Start a mission once, returning its existing active progress on retries."""
        mission = self.get_mission(mission_id)
        progress = self.progress_repo.get_by_user_and_mission(user_id, mission_id)
        if progress is not None and progress.status == "completed":
            raise ConflictException("A completed mission cannot be started again.")
        if progress is not None and progress.status == "in_progress":
            return progress

        now = datetime.now(UTC)
        if progress is None:
            progress = PlayerProgress(
                user_id=user_id,
                chapter_id=mission.chapter_id,
                mission_id=mission_id,
                status="in_progress",
                started_at=now,
            )
        else:
            progress.status = "in_progress"
            progress.started_at = progress.started_at or now
        return self.progress_repo.save(progress)

    def submit_mission(
        self,
        user_id: uuid.UUID,
        mission_id: uuid.UUID,
        submission: dict[str, Any],
    ) -> tuple[PlayerProgress, Mission, bool]:
        """Score a started mission using its authored answer rules, never client input."""
        mission = self.get_mission(mission_id)
        progress = self.progress_repo.get_by_user_and_mission(user_id, mission_id)
        if progress is None or progress.status != "in_progress":
            raise ConflictException("Start the mission before submitting an answer.")

        choice = submission.get("choice")
        score_breakdown = mission.answer_rules.get("score_breakdown")
        if not isinstance(choice, str) or not isinstance(score_breakdown, dict):
            raise ConflictException("This mission has no supported choice-based answer rules.")
        if choice not in score_breakdown:
            raise ValidationException(
                "The submitted choice is not available for this mission.",
                details={"mission_id": str(mission_id)},
            )

        raw_score = score_breakdown[choice]
        if not isinstance(raw_score, int) or isinstance(raw_score, bool):
            raise ConflictException("Mission answer rules contain an invalid score.")
        score = min(max(raw_score, 0), mission.max_score)
        recommended_choice = mission.answer_rules.get("recommended_choice")

        progress.status = "completed"
        progress.score = score
        progress.attempts += 1
        progress.submission_data = {**progress.submission_data, **submission}
        progress.completed_at = datetime.now(UTC)
        self.progress_repo.save(progress)
        return progress, mission, choice == recommended_choice

    def save_field_observation(
        self,
        user_id: uuid.UUID,
        mission_id: uuid.UUID,
        observation: dict[str, Any],
    ) -> PlayerProgress:
        """Store a farmer's observation without treating it as satellite evidence."""
        self.get_mission(mission_id)
        progress = self.progress_repo.get_by_user_and_mission(user_id, mission_id)
        if progress is None or progress.status != "in_progress":
            raise ConflictException("Start the mission before recording a field observation.")

        progress.submission_data = {
            **progress.submission_data,
            "field_observation": observation,
        }
        return self.progress_repo.save(progress)

    def list_progress(
        self,
        user_id: uuid.UUID,
        limit: int,
        offset: int,
    ) -> tuple[list[PlayerProgress], int]:
        """Return a page of a player's progress and its total count."""
        items = self.progress_repo.list_page_by_user(user_id, limit, offset)
        total = self.progress_repo.count_by_user(user_id)
        return items, total

    def list_achievements(self, user_id: uuid.UUID) -> list[AchievementRead]:
        """Return the achievement catalog annotated with this player's unlocks."""
        unlocked_ids = {
            achievement.id for achievement in self.achievement_repo.get_user_achievements(user_id)
        }
        return [
            AchievementRead(
                id=achievement.id,
                code=achievement.code,
                title=achievement.title,
                description=achievement.description,
                badge_icon=achievement.badge_icon,
                unlocked=achievement.id in unlocked_ids,
            )
            for achievement in self.achievement_repo.list()
        ]

    def get_content_manifest(
        self,
        language: str,
        region_id: uuid.UUID | None,
    ) -> list[ContentManifestItem]:
        """List only verified content approved for publication."""
        lessons = self.lesson_repo.list_verified_for_manifest(language, region_id)
        missions = self.mission_repo.list_verified_for_manifest(language, region_id)
        published_chapters = (
            self.content_status_repo.list_published_chapter_ids(region_id)
            if region_id is not None
            else set()
        )

        items: list[ContentManifestItem] = []
        for lesson in lessons:
            if lesson.region_id is not None and lesson.chapter_id not in published_chapters:
                continue
            items.append(
                ContentManifestItem(
                    id=lesson.id,
                    chapter_id=lesson.chapter_id,
                    content_type="lesson",
                    position=lesson.position,
                    language=lesson.language,
                    content_version=lesson.content_version,
                    is_synthetic=lesson.is_synthetic,
                )
            )
        for mission in missions:
            if mission.region_id is not None and mission.chapter_id not in published_chapters:
                continue
            items.append(
                ContentManifestItem(
                    id=mission.id,
                    chapter_id=mission.chapter_id,
                    content_type="mission",
                    position=mission.position,
                    language=mission.language,
                    content_version=mission.content_version,
                    is_synthetic=mission.is_synthetic,
                )
            )
        return sorted(
            items,
            key=lambda item: (str(item.chapter_id), item.position, item.content_type),
        )
