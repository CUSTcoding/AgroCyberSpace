"""create district crop stats and soil units tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-15 15:30:00.000000

"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. district_crop_stats table
    op.create_table(
        "district_crop_stats",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("district_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("crop", sa.String(length=50), nullable=False),
        sa.Column("area_ha", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column("production_t", sa.Float(), server_default=sa.text("0.0"), nullable=False),
        sa.Column(
            "campaign",
            sa.String(length=50),
            server_default=sa.text("'2023/2024'"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), server_default=sa.text("2023"), nullable=False),
        sa.Column(
            "source",
            sa.String(length=100),
            server_default=sa.text("'INE/MADER - CAP 2023/2024'"),
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
        sa.ForeignKeyConstraint(["district_id"], ["districts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_district_crop_stats_district_id",
        "district_crop_stats",
        ["district_id"],
        unique=False,
    )
    op.create_index(
        "ix_district_crop_stats_crop",
        "district_crop_stats",
        ["crop"],
        unique=False,
    )

    # 2. soil_units table
    op.create_table(
        "soil_units",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "properties",
            JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=100),
            server_default=sa.text("'INIA/IIAM 1995'"),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), server_default=sa.text("1995"), nullable=False),
        sa.Column(
            "boundary",
            geoalchemy2.types.Geometry(
                geometry_type="GEOMETRY",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
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
    op.create_index(
        "ix_soil_units_code",
        "soil_units",
        ["code"],
        unique=True,
    )
    op.create_index(
        "idx_soil_units_boundary",
        "soil_units",
        ["boundary"],
        unique=False,
        postgresql_using="gist",
    )


def downgrade() -> None:
    op.drop_index("idx_soil_units_boundary", table_name="soil_units", postgresql_using="gist")
    op.drop_index("ix_soil_units_code", table_name="soil_units")
    op.drop_table("soil_units")
    op.drop_index("ix_district_crop_stats_crop", table_name="district_crop_stats")
    op.drop_index("ix_district_crop_stats_district_id", table_name="district_crop_stats")
    op.drop_table("district_crop_stats")
