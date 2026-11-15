"""create game system tables (chapters, lessons, missions, progress, achievements)

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-15 16:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. chapters table
    op.create_table(
        "chapters",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("chapter_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("learning_objective", sa.Text(), nullable=False),
        sa.Column("is_common", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "unlock_rule",
            JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "topics",
            JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("order", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("provisional", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chapters_chapter_number", "chapters", ["chapter_number"], unique=True)

    # 2. lessons table
    op.create_table(
        "lessons",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("chapter_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("region_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("position", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("topic", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("text_simple", sa.Text(), nullable=False),
        sa.Column("audio_text", sa.Text(), nullable=False),
        sa.Column(
            "learning_points",
            JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "evidence",
            JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("source", sa.String(length=150), nullable=False),
        sa.Column("verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "language",
            sa.String(length=10),
            server_default=sa.text("'pt'"),
            nullable=False,
        ),
        sa.Column("content_version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lessons_chapter_id", "lessons", ["chapter_id"], unique=False)
    op.create_index("ix_lessons_region_id", "lessons", ["region_id"], unique=False)

    # 3. missions table
    op.create_table(
        "missions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("chapter_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("region_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("position", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("mission_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("prompt_simple", sa.Text(), nullable=False),
        sa.Column(
            "configuration",
            JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "answer_rules",
            JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("learning_note", sa.Text(), nullable=False),
        sa.Column("max_score", sa.Integer(), server_default=sa.text("100"), nullable=False),
        sa.Column("verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "language",
            sa.String(length=10),
            server_default=sa.text("'pt'"),
            nullable=False,
        ),
        sa.Column("content_version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_missions_chapter_id", "missions", ["chapter_id"], unique=False)
    op.create_index("ix_missions_region_id", "missions", ["region_id"], unique=False)

    # 4. player_progress table
    op.create_table(
        "player_progress",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("chapter_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("lesson_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("mission_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default=sa.text("'not_started'"),
            nullable=False,
        ),
        sa.Column("score", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("attempts", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "submission_data",
            JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mission_id"], ["missions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_player_progress_user_id", "player_progress", ["user_id"], unique=False)
    op.create_index(
        "ix_player_progress_chapter_id", "player_progress", ["chapter_id"], unique=False
    )
    op.create_index("ix_player_progress_lesson_id", "player_progress", ["lesson_id"], unique=False)
    op.create_index(
        "ix_player_progress_mission_id", "player_progress", ["mission_id"], unique=False
    )

    # 5. achievements table
    op.create_table(
        "achievements",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "badge_icon",
            sa.String(length=100),
            server_default=sa.text("'badge_default'"),
            nullable=False,
        ),
        sa.Column(
            "criteria",
            JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_achievements_code", "achievements", ["code"], unique=True)

    # 6. user_achievements table
    op.create_table(
        "user_achievements",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("achievement_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column(
            "unlocked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["achievement_id"], ["achievements.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "achievement_id", name="uq_user_achievements_user_achievement"
        ),
    )
    op.create_index("ix_user_achievements_user_id", "user_achievements", ["user_id"], unique=False)
    op.create_index(
        "ix_user_achievements_achievement_id",
        "user_achievements",
        ["achievement_id"],
        unique=False,
    )

    # 7. region_content_status table
    op.create_table(
        "region_content_status",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("region_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("chapter_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("lessons_total", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("lessons_verified", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("missions_total", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column(
            "status",
            sa.String(length=30),
            server_default=sa.text("'draft'"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "region_id", "chapter_id", name="uq_region_content_status_region_chapter"
        ),
    )
    op.create_index(
        "ix_region_content_status_region_id",
        "region_content_status",
        ["region_id"],
        unique=False,
    )
    op.create_index(
        "ix_region_content_status_chapter_id",
        "region_content_status",
        ["chapter_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_region_content_status_chapter_id", table_name="region_content_status")
    op.drop_index("ix_region_content_status_region_id", table_name="region_content_status")
    op.drop_table("region_content_status")

    op.drop_index("ix_user_achievements_achievement_id", table_name="user_achievements")
    op.drop_index("ix_user_achievements_user_id", table_name="user_achievements")
    op.drop_table("user_achievements")

    op.drop_index("ix_achievements_code", table_name="achievements")
    op.drop_table("achievements")

    op.drop_index("ix_player_progress_mission_id", table_name="player_progress")
    op.drop_index("ix_player_progress_lesson_id", table_name="player_progress")
    op.drop_index("ix_player_progress_chapter_id", table_name="player_progress")
    op.drop_index("ix_player_progress_user_id", table_name="player_progress")
    op.drop_table("player_progress")

    op.drop_index("ix_missions_region_id", table_name="missions")
    op.drop_index("ix_missions_chapter_id", table_name="missions")
    op.drop_table("missions")

    op.drop_index("ix_lessons_region_id", table_name="lessons")
    op.drop_index("ix_lessons_chapter_id", table_name="lessons")
    op.drop_table("lessons")

    op.drop_index("ix_chapters_chapter_number", table_name="chapters")
    op.drop_table("chapters")
