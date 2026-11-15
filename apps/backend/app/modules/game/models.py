"""ORM models for game chapters, lessons, missions, player progress, and achievements."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Chapter(Base):
    """Educational game chapter (1 to 12)."""

    __tablename__ = "chapters"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    chapter_number: Mapped[int] = mapped_column(
        Integer,
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    learning_objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    is_common: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    unlock_rule: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    topics: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    order: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    provisional: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    lessons: Mapped[list[Lesson]] = relationship(
        "Lesson",
        back_populates="chapter",
        cascade="all, delete-orphan",
    )
    missions: Mapped[list[Mission]] = relationship(
        "Mission",
        back_populates="chapter",
        cascade="all, delete-orphan",
    )

    def __init__(
        self,
        chapter_number: int,
        title: str,
        learning_objective: str,
        is_common: bool = False,
        unlock_rule: dict[str, Any] | None = None,
        topics: list[str] | None = None,
        order: int | None = None,
        provisional: bool = True,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.chapter_number = chapter_number
        self.title = title
        self.learning_objective = learning_objective
        self.is_common = is_common
        self.unlock_rule = unlock_rule or {}
        self.topics = topics or []
        self.order = order or chapter_number
        self.provisional = provisional
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<Chapter #{self.chapter_number} {self.title!r}>"


class Lesson(Base):
    """Educational lesson/teaching material within a chapter."""

    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    region_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("regions.id", ondelete="CASCADE"),
        index=True,
        nullable=True,  # null for common lessons (chapters 1 & 2)
    )
    position: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    topic: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    text_simple: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    audio_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    learning_points: Mapped[list[str]] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )
    evidence: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    source: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_synthetic: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    language: Mapped[str] = mapped_column(
        String(10),
        default="pt",
        nullable=False,
    )
    content_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    chapter: Mapped[Chapter] = relationship("Chapter", back_populates="lessons")

    def __init__(
        self,
        chapter_id: uuid.UUID,
        topic: str,
        title: str,
        text_simple: str,
        audio_text: str,
        source: str,
        region_id: uuid.UUID | None = None,
        position: int = 1,
        learning_points: list[str] | None = None,
        evidence: dict[str, Any] | None = None,
        verified: bool = False,
        is_synthetic: bool = False,
        language: str = "pt",
        content_version: int = 1,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.chapter_id = chapter_id
        self.region_id = region_id
        self.position = position
        self.topic = topic
        self.title = title
        self.text_simple = text_simple
        self.audio_text = audio_text
        self.learning_points = learning_points or []
        self.evidence = evidence or {}
        self.source = source
        self.verified = verified
        self.is_synthetic = is_synthetic
        self.language = language
        self.content_version = content_version
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<Lesson {self.title!r} (ch={self.chapter_id})>"


class Mission(Base):
    """Practical agricultural challenge or decision mission within a chapter."""

    __tablename__ = "missions"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    region_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("regions.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    mission_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    prompt_simple: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    configuration: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    answer_rules: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    learning_note: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    max_score: Mapped[int] = mapped_column(
        Integer,
        default=100,
        nullable=False,
    )
    verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_synthetic: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    language: Mapped[str] = mapped_column(
        String(10),
        default="pt",
        nullable=False,
    )
    content_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    chapter: Mapped[Chapter] = relationship("Chapter", back_populates="missions")

    def __init__(
        self,
        chapter_id: uuid.UUID,
        mission_type: str,
        title: str,
        prompt_simple: str,
        learning_note: str,
        region_id: uuid.UUID | None = None,
        position: int = 1,
        configuration: dict[str, Any] | None = None,
        answer_rules: dict[str, Any] | None = None,
        max_score: int = 100,
        verified: bool = False,
        is_synthetic: bool = False,
        language: str = "pt",
        content_version: int = 1,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.chapter_id = chapter_id
        self.region_id = region_id
        self.position = position
        self.mission_type = mission_type
        self.title = title
        self.prompt_simple = prompt_simple
        self.configuration = configuration or {}
        self.answer_rules = answer_rules or {}
        self.learning_note = learning_note
        self.max_score = max_score
        self.verified = verified
        self.is_synthetic = is_synthetic
        self.language = language
        self.content_version = content_version
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<Mission {self.title!r} (type={self.mission_type})>"


class PlayerProgress(Base):
    """Progress records for players completing lessons and missions."""

    __tablename__ = "player_progress"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    mission_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("missions.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="not_started",
        nullable=False,
    )
    score: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    submission_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __init__(
        self,
        user_id: uuid.UUID,
        chapter_id: uuid.UUID,
        lesson_id: uuid.UUID | None = None,
        mission_id: uuid.UUID | None = None,
        status: str = "not_started",
        score: int = 0,
        attempts: int = 0,
        submission_data: dict[str, Any] | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.user_id = user_id
        self.chapter_id = chapter_id
        self.lesson_id = lesson_id
        self.mission_id = mission_id
        self.status = status
        self.score = score
        self.attempts = attempts
        self.submission_data = submission_data or {}
        self.started_at = started_at
        self.completed_at = completed_at
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<PlayerProgress user={self.user_id} status={self.status}>"


class Achievement(Base):
    """Badge or accomplishment attainable by players."""

    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    badge_icon: Mapped[str] = mapped_column(
        String(100),
        default="badge_default",
        nullable=False,
    )
    criteria: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __init__(
        self,
        code: str,
        title: str,
        description: str,
        badge_icon: str = "badge_default",
        criteria: dict[str, Any] | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.code = code
        self.title = title
        self.description = description
        self.badge_icon = badge_icon
        self.criteria = criteria or {}
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<Achievement {self.code!r}>"


class UserAchievement(Base):
    """Link table between user and unlocked achievement."""

    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievements_user_achievement"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("achievements.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Relationships
    achievement: Mapped[Achievement] = relationship("Achievement")

    def __init__(
        self,
        user_id: uuid.UUID,
        achievement_id: uuid.UUID,
        unlocked_at: datetime | None = None,
        id: uuid.UUID | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.user_id = user_id
        self.achievement_id = achievement_id
        self.unlocked_at = unlocked_at or datetime.now(UTC)

    def __repr__(self) -> str:
        return f"<UserAchievement user={self.user_id} achievement={self.achievement_id}>"


class RegionContentStatus(Base):
    """Tracks publication and verification state of content for a specific region and chapter."""

    __tablename__ = "region_content_status"
    __table_args__ = (
        UniqueConstraint("region_id", "chapter_id", name="uq_region_content_status_region_chapter"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    region_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("regions.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    lessons_total: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    lessons_verified: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    missions_total: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default="draft",
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __init__(
        self,
        region_id: uuid.UUID,
        chapter_id: uuid.UUID,
        lessons_total: int = 0,
        lessons_verified: int = 0,
        missions_total: int = 0,
        status: str = "draft",
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.region_id = region_id
        self.chapter_id = chapter_id
        self.lessons_total = lessons_total
        self.lessons_verified = lessons_verified
        self.missions_total = missions_total
        self.status = status
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<RegionContentStatus region={self.region_id} ch={self.chapter_id} {self.status}>"
