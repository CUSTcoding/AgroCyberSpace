"""Geospatial ORM models for Regions, Districts, and Communities."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Region(Base):
    """Study region or provincial target area."""

    __tablename__ = "regions"

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
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    boundary: Mapped[Any] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True),
        nullable=True,
    )
    is_proposed_study_area: Mapped[bool] = mapped_column(
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
    districts: Mapped[list[District]] = relationship(
        "District",
        back_populates="region",
        cascade="all, delete-orphan",
    )

    def __init__(
        self,
        code: str,
        name: str,
        description: str | None = None,
        boundary: Any = None,
        is_proposed_study_area: bool = True,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.code = code
        self.name = name
        self.description = description
        self.boundary = boundary
        self.is_proposed_study_area = is_proposed_study_area
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<Region id={self.id} code={self.code!r} name={self.name!r}>"


class District(Base):
    """Administrative district level (based on CENACARTA 2017)."""

    __tablename__ = "districts"

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
    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    province: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    boundary: Mapped[Any] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True),
        nullable=True,
    )
    source: Mapped[str] = mapped_column(
        String(100),
        default="CENACARTA 2017",
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
    region: Mapped[Region] = relationship("Region", back_populates="districts")
    communities: Mapped[list[Community]] = relationship(
        "Community",
        back_populates="district",
        cascade="all, delete-orphan",
    )

    def __init__(
        self,
        region_id: uuid.UUID,
        code: str,
        name: str,
        province: str,
        boundary: Any = None,
        source: str = "CENACARTA 2017",
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.region_id = region_id
        self.code = code
        self.name = name
        self.province = province
        self.boundary = boundary
        self.source = source
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<District id={self.id} code={self.code!r} name={self.name!r}>"


class Community(Base):
    """Local agricultural community or settlement."""

    __tablename__ = "communities"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    district_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("districts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    location: Mapped[Any] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
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

    # Relationships
    district: Mapped[District] = relationship("District", back_populates="communities")

    def __init__(
        self,
        district_id: uuid.UUID,
        name: str,
        location: Any = None,
        description: str | None = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.district_id = district_id
        self.name = name
        self.location = location
        self.description = description
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<Community id={self.id} name={self.name!r}>"
