"""Persisted Earth Observation dataset metadata and point indicators."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Dataset(Base):
    """Versioned source dataset metadata; no raster pixels are stored here."""

    __tablename__ = "datasets"
    __table_args__ = (
        UniqueConstraint(
            "source",
            "product",
            "variable",
            "version",
            name="uq_datasets_source_product_variable_version",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    product: Mapped[str] = mapped_column(String(120), nullable=False)
    variable: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(80), nullable=False)
    spatial_resolution: Mapped[str] = mapped_column(String(160), nullable=False)
    temporal_resolution: Mapped[str] = mapped_column(String(80), nullable=False)
    quality_notes: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )
    license: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def __init__(
        self,
        source: str,
        product: str,
        variable: str,
        version: str,
        spatial_resolution: str,
        temporal_resolution: str,
        quality_notes: str,
        metadata_json: dict[str, Any] | None = None,
        license: str | None = None,
        is_synthetic: bool = False,
        id: uuid.UUID | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.source = source
        self.product = product
        self.variable = variable
        self.version = version
        self.spatial_resolution = spatial_resolution
        self.temporal_resolution = temporal_resolution
        self.quality_notes = quality_notes
        self.metadata_json = metadata_json or {}
        self.license = license
        self.is_synthetic = is_synthetic
        now = datetime.now(UTC)
        self.created_at = now
        self.updated_at = now


class Indicator(Base):
    """One dated value at a source grid point, linked to its dataset version."""

    __tablename__ = "indicators"
    __table_args__ = (
        UniqueConstraint(
            "dataset_id",
            "region_id",
            "longitude",
            "latitude",
            "observed_at",
            name="uq_indicators_dataset_region_point_date",
        ),
        Index("ix_indicators_region_type_date", "region_id", "indicator_type", "observed_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    region_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("regions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("datasets.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    indicator_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    observed_at: Mapped[date] = mapped_column(Date, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(30), default="derived", nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    def __init__(
        self,
        region_id: uuid.UUID,
        dataset_id: uuid.UUID,
        indicator_type: str,
        value: float,
        unit: str,
        observed_at: date,
        latitude: float,
        longitude: float,
        category: str = "derived",
        is_synthetic: bool = False,
        id: uuid.UUID | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.region_id = region_id
        self.dataset_id = dataset_id
        self.indicator_type = indicator_type
        self.value = value
        self.unit = unit
        self.observed_at = observed_at
        self.latitude = latitude
        self.longitude = longitude
        self.category = category
        self.is_synthetic = is_synthetic
        self.created_at = datetime.now(UTC)


class IngestionRun(Base):
    """Audit record for a repeatable external data ingestion run."""

    __tablename__ = "ingestion_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("datasets.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    region_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("regions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    product: Mapped[str] = mapped_column(String(120), nullable=False)
    version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    time_start: Mapped[date] = mapped_column(Date, nullable=False)
    time_end: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="running")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
