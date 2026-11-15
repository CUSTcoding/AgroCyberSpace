"""create datasets, point indicators, and ingestion run tables

Revision ID: 0006
Revises: 0005
Create Date: 2026-11-15
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "datasets",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("product", sa.String(120), nullable=False),
        sa.Column("variable", sa.String(100), nullable=False),
        sa.Column("version", sa.String(80), nullable=False),
        sa.Column("spatial_resolution", sa.String(160), nullable=False),
        sa.Column("temporal_resolution", sa.String(80), nullable=False),
        sa.Column("quality_notes", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("license", sa.Text(), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), server_default=sa.text("false"), nullable=False),
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
        sa.UniqueConstraint(
            "source",
            "product",
            "variable",
            "version",
            name="uq_datasets_source_product_variable_version",
        ),
    )
    op.create_index("ix_datasets_source", "datasets", ["source"])
    op.create_index("ix_datasets_variable", "datasets", ["variable"])

    op.create_table(
        "indicators",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("region_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("dataset_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("indicator_type", sa.String(100), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(50), nullable=False),
        sa.Column("observed_at", sa.Date(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("category", sa.String(30), server_default="derived", nullable=False),
        sa.Column("is_synthetic", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "dataset_id",
            "region_id",
            "longitude",
            "latitude",
            "observed_at",
            name="uq_indicators_dataset_region_point_date",
        ),
    )
    op.create_index(
        "ix_indicators_region_type_date",
        "indicators",
        ["region_id", "indicator_type", "observed_at"],
    )
    op.create_index("ix_indicators_region_id", "indicators", ["region_id"])
    op.create_index("ix_indicators_dataset_id", "indicators", ["dataset_id"])

    op.create_table(
        "ingestion_runs",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("dataset_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("region_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("product", sa.String(120), nullable=False),
        sa.Column("version", sa.String(80), nullable=True),
        sa.Column("time_start", sa.Date(), nullable=False),
        sa.Column("time_end", sa.Date(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("checksum", sa.String(64), nullable=True),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["dataset_id"], ["datasets.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["region_id"], ["regions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ingestion_runs_region_id", "ingestion_runs", ["region_id"])
    op.create_index("ix_ingestion_runs_dataset_id", "ingestion_runs", ["dataset_id"])


def downgrade() -> None:
    op.drop_index("ix_ingestion_runs_dataset_id", table_name="ingestion_runs")
    op.drop_index("ix_ingestion_runs_region_id", table_name="ingestion_runs")
    op.drop_table("ingestion_runs")
    op.drop_index("ix_indicators_dataset_id", table_name="indicators")
    op.drop_index("ix_indicators_region_id", table_name="indicators")
    op.drop_index("ix_indicators_region_type_date", table_name="indicators")
    op.drop_table("indicators")
    op.drop_index("ix_datasets_variable", table_name="datasets")
    op.drop_index("ix_datasets_source", table_name="datasets")
    op.drop_table("datasets")
