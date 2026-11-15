"""FastAPI router for game chapters, lessons, and missions."""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUser
from app.modules.game.schemas import (
    AchievementListResponse,
    ChapterDetail,
    ChapterListResponse,
    ContentManifestResponse,
    FieldObservation,
    LessonRead,
    MissionListResponse,
    MissionRead,
    MissionSubmission,
    MissionSubmissionResult,
    ProgressListResponse,
    ProgressRead,
)
from app.modules.game.service import GameService

router = APIRouter(prefix="/game", tags=["Game"])
content_router = APIRouter(tags=["Content"])


def get_game_service(db: Annotated[Session, Depends(get_db)]) -> GameService:
    """Dependency provider for GameService."""
    return GameService(db)


@router.get(
    "/chapters",
    response_model=ChapterListResponse,
    summary="List all game chapters",
    description="Retrieve the 12 game chapters with unlock status and summary objectives.",
)
def list_chapters(
    current_user: CurrentUser,
    service: Annotated[GameService, Depends(get_game_service)],
    region_id: Annotated[uuid.UUID | None, Query(description="Optional region UUID filter")] = None,
) -> ChapterListResponse:
    """List chapters."""
    items = service.list_chapters(
        user_id=current_user.id,
        region_id=region_id or current_user.selected_region_id,
    )
    return ChapterListResponse(items=items, total=len(items))


@router.get(
    "/chapters/{chapter_id}",
    response_model=ChapterDetail,
    summary="Get chapter detail with lessons and missions",
    description="Retrieve a single chapter's learning objective, ordered lessons, and missions.",
)
def get_chapter(
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    service: Annotated[GameService, Depends(get_game_service)],
    region_id: Annotated[uuid.UUID | None, Query(description="Target region UUID")] = None,
) -> ChapterDetail:
    """Fetch chapter with lessons and missions."""
    return service.get_chapter(
        chapter_id,
        user_id=current_user.id,
        region_id=region_id or current_user.selected_region_id,
    )


@router.get(
    "/lessons/{lesson_id}",
    response_model=LessonRead,
    summary="Get lesson details",
    description="Retrieve educational lesson content, teaching points, and scientific sources.",
)
def get_lesson(
    lesson_id: uuid.UUID,
    service: Annotated[GameService, Depends(get_game_service)],
) -> LessonRead:
    """Fetch single lesson."""
    lesson = service.get_lesson(lesson_id)
    return LessonRead.model_validate(lesson)


@router.get(
    "/missions",
    response_model=MissionListResponse,
    summary="List missions (challenges)",
    description=(
        "Retrieve available agricultural challenges, optionally filtered by chapter or region."
    ),
)
def list_missions(
    service: Annotated[GameService, Depends(get_game_service)],
    chapter_id: Annotated[uuid.UUID | None, Query(description="Chapter UUID filter")] = None,
    region_id: Annotated[uuid.UUID | None, Query(description="Region UUID filter")] = None,
) -> MissionListResponse:
    """List missions."""
    items = service.list_missions(chapter_id=chapter_id, region_id=region_id)
    return MissionListResponse(
        items=[MissionRead.model_validate(m) for m in items],
        total=len(items),
    )


@router.get(
    "/missions/{mission_id}",
    response_model=MissionRead,
    summary="Get mission details",
    description="Retrieve a specific agricultural decision challenge without the answer key.",
)
def get_mission(
    mission_id: uuid.UUID,
    service: Annotated[GameService, Depends(get_game_service)],
) -> MissionRead:
    """Fetch single mission."""
    mission = service.get_mission(mission_id)
    return MissionRead.model_validate(mission)


@router.post(
    "/lessons/{lesson_id}/complete",
    response_model=ProgressRead,
    summary="Complete a lesson",
)
def complete_lesson(
    lesson_id: uuid.UUID,
    current_user: CurrentUser,
    service: Annotated[GameService, Depends(get_game_service)],
) -> ProgressRead:
    """Record completion of a lesson for the authenticated player."""
    progress = service.complete_lesson(current_user.id, lesson_id)
    return ProgressRead.model_validate(progress)


@router.post(
    "/missions/{mission_id}/start",
    response_model=ProgressRead,
    summary="Start a mission",
)
def start_mission(
    mission_id: uuid.UUID,
    current_user: CurrentUser,
    service: Annotated[GameService, Depends(get_game_service)],
) -> ProgressRead:
    """Start a mission for the authenticated player."""
    progress = service.start_mission(current_user.id, mission_id)
    return ProgressRead.model_validate(progress)


@router.post(
    "/missions/{mission_id}/submit",
    response_model=MissionSubmissionResult,
    summary="Submit a mission answer",
)
def submit_mission(
    mission_id: uuid.UUID,
    submission: MissionSubmission,
    current_user: CurrentUser,
    service: Annotated[GameService, Depends(get_game_service)],
) -> MissionSubmissionResult:
    """Validate and score an answer using the mission's authored rules."""
    progress, mission, is_recommended = service.submit_mission(
        current_user.id,
        mission_id,
        submission.model_dump(),
    )
    return MissionSubmissionResult(
        progress=ProgressRead.model_validate(progress),
        score=progress.score,
        max_score=mission.max_score,
        is_recommended=is_recommended,
        learning_note=mission.learning_note,
    )


@router.post(
    "/missions/{mission_id}/field-observation",
    response_model=ProgressRead,
    summary="Record a field observation",
)
def save_field_observation(
    mission_id: uuid.UUID,
    observation: FieldObservation,
    current_user: CurrentUser,
    service: Annotated[GameService, Depends(get_game_service)],
) -> ProgressRead:
    """Record the player's observation separately from remotely sensed data."""
    progress = service.save_field_observation(
        current_user.id,
        mission_id,
        observation.model_dump(exclude_none=True),
    )
    return ProgressRead.model_validate(progress)


@router.get("/progress", response_model=ProgressListResponse, summary="Get player progress")
def list_progress(
    current_user: CurrentUser,
    service: Annotated[GameService, Depends(get_game_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ProgressListResponse:
    """Return the authenticated player's paginated progress."""
    items, total = service.list_progress(current_user.id, limit, offset)
    return ProgressListResponse(
        items=[ProgressRead.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/achievements",
    response_model=AchievementListResponse,
    summary="Get achievements and unlock status",
)
def list_achievements(
    current_user: CurrentUser,
    service: Annotated[GameService, Depends(get_game_service)],
) -> AchievementListResponse:
    """Return the achievement catalog and this player's unlock state."""
    items = service.list_achievements(current_user.id)
    return AchievementListResponse(items=items, total=len(items))


@content_router.get("/content/manifest", response_model=ContentManifestResponse)
def get_content_manifest(
    service: Annotated[GameService, Depends(get_game_service)],
    region_id: uuid.UUID | None = None,
    language: Literal["pt", "en"] = "pt",
) -> ContentManifestResponse:
    """Return a compact manifest of verified, published content."""
    items = service.get_content_manifest(language=language, region_id=region_id)
    return ContentManifestResponse(
        region_id=region_id,
        language=language,
        items=items,
        total=len(items),
    )
