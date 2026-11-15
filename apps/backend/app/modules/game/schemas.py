"""Pydantic v2 schemas for game chapters, lessons, missions, and progress."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LessonRead(BaseModel):
    """Schema for lesson details returned to players."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chapter_id: uuid.UUID
    region_id: uuid.UUID | None = None
    position: int
    topic: str
    title: str
    text_simple: str
    audio_text: str
    learning_points: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
    source: str
    verified: bool
    is_synthetic: bool
    language: str
    content_version: int


class MissionRead(BaseModel):
    """Schema for mission (challenge) details returned to players (omits answer_rules)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chapter_id: uuid.UUID
    region_id: uuid.UUID | None = None
    position: int
    mission_type: str
    title: str
    prompt_simple: str
    configuration: dict[str, Any] = Field(default_factory=dict)
    learning_note: str
    max_score: int
    verified: bool
    is_synthetic: bool
    language: str
    content_version: int


class ChapterSummary(BaseModel):
    """Overview schema for a chapter in listings."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chapter_number: int
    title: str
    learning_objective: str
    is_common: bool
    topics: list[str]
    order: int
    provisional: bool
    is_unlocked: bool = True


class ChapterDetail(ChapterSummary):
    """Detailed chapter schema including lessons and missions for a specific region."""

    lessons: list[LessonRead] = Field(default_factory=list)
    missions: list[MissionRead] = Field(default_factory=list)


class ChapterListResponse(BaseModel):
    """Paginated list of chapters."""

    items: list[ChapterSummary]
    total: int


class MissionListResponse(BaseModel):
    """List of missions response."""

    items: list[MissionRead]
    total: int


class ProgressRead(BaseModel):
    """Player progress for one lesson or mission."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chapter_id: uuid.UUID
    lesson_id: uuid.UUID | None
    mission_id: uuid.UUID | None
    status: str
    score: int
    attempts: int
    started_at: datetime | None
    completed_at: datetime | None


class ProgressListResponse(BaseModel):
    """Paginated player progress response."""

    items: list[ProgressRead]
    total: int
    limit: int
    offset: int


class AchievementRead(BaseModel):
    """Achievement catalog item with the current player's unlock state."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    title: str
    description: str
    badge_icon: str
    unlocked: bool


class AchievementListResponse(BaseModel):
    """Available achievements and unlock states for one player."""

    items: list[AchievementRead]
    total: int


class ContentManifestItem(BaseModel):
    """Small versioned reference to verified, published game content."""

    id: uuid.UUID
    chapter_id: uuid.UUID
    content_type: str
    position: int
    language: str
    content_version: int
    is_synthetic: bool


class ContentManifestResponse(BaseModel):
    """Lightweight content manifest for offline clients."""

    region_id: uuid.UUID | None
    language: str
    items: list[ContentManifestItem]
    total: int


class MissionSubmission(BaseModel):
    """Submission data for a choice-based seeded mission."""

    choice: str = Field(min_length=1, max_length=500)


class FieldObservation(BaseModel):
    """Simple farmer observation recorded alongside mission progress."""

    observed_condition: str = Field(min_length=1, max_length=500)
    note: str | None = Field(default=None, max_length=1000)


class MissionSubmissionResult(BaseModel):
    """Scored mission submission with its learning note."""

    progress: ProgressRead
    score: int
    max_score: int
    is_recommended: bool
    learning_note: str
