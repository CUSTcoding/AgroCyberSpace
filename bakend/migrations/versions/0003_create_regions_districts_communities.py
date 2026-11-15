"""create regions districts communities tables

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-15 14:00:00.000000

"""

from collections.abc import Sequence

import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Regions table
    op.create_table(
        "regions",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
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
            "is_proposed_study_area",
            sa.Boolean(),
            server_default=sa.text("true"),
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
        sa.PrimaryKeyConstraint("id", name="pk_regions"),
    )
    op.create_index("ix_regions_code", "regions", ["code"], unique=True)
    op.create_index(
        "idx_regions_boundary",
        "regions",
        ["boundary"],
        unique=False,
        postgresql_using="gist",
    )

    # 2. Districts table
    op.create_table(
        "districts",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("region_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("province", sa.String(length=100), nullable=False),
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
            "source",
            sa.String(length=100),
            server_default="CENACARTA 2017",
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
        sa.ForeignKeyConstraint(
            ["region_id"],
            ["regions.id"],
            name="fk_districts_region_id_regions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_districts"),
    )
    op.create_index("ix_districts_code", "districts", ["code"], unique=True)
    op.create_index("ix_districts_region_id", "districts", ["region_id"], unique=False)
    op.create_index(
        "idx_districts_boundary",
        "districts",
        ["boundary"],
        unique=False,
        postgresql_using="gist",
    )

    # 3. Communities table
    op.create_table(
        "communities",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("district_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "location",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
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
        sa.ForeignKeyConstraint(
            ["district_id"],
            ["districts.id"],
            name="fk_communities_district_id_districts",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_communities"),
    )
    op.create_index("ix_communities_district_id", "communities", ["district_id"], unique=False)
    op.create_index(
        "idx_communities_location",
        "communities",
        ["location"],
        unique=False,
        postgresql_using="gist",
    )

    # 4. Link users.selected_region_id FK
    op.create_foreign_key(
        "fk_users_selected_region_id_regions",
        "users",
        "regions",
        ["selected_region_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_users_selected_region_id_regions", "users", type_="foreignkey")
    op.drop_index("idx_communities_location", table_name="communities", postgresql_using="gist")
    op.drop_index("ix_communities_district_id", table_name="communities")
    op.drop_table("communities")

    op.drop_index("idx_districts_boundary", table_name="districts", postgresql_using="gist")
    op.drop_index("ix_districts_region_id", table_name="districts")
    op.drop_index("ix_districts_code", table_name="districts")
    op.drop_table("districts")

    op.drop_index("idx_regions_boundary", table_name="regions", postgresql_using="gist")
    op.drop_index("ix_regions_code", table_name="regions")
    op.drop_table("regions")
