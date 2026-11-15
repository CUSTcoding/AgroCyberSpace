"""Agricultural ORM models for district crop statistics and national soil units."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from geoalchemy2 import Geometry
from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DistrictCropStat(Base):
    """District level crop area and production statistics (INE / MADER CAP 2023/2024)."""

    __tablename__ = "district_crop_stats"

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
    crop: Mapped[str] = mapped_column(
        String(50),
        index=True,
        nullable=False,
    )
    area_ha: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    production_t: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    campaign: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="2023/2024",
    )
    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2023,
    )
    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="INE/MADER - CAP 2023/2024",
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
    district: Mapped[Any] = relationship("District")

    def __init__(
        self,
        district_id: uuid.UUID,
        crop: str,
        area_ha: float,
        production_t: float,
        campaign: str = "2023/2024",
        year: int = 2023,
        source: str = "INE/MADER - CAP 2023/2024",
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.district_id = district_id
        self.crop = crop
        self.area_ha = area_ha
        self.production_t = production_t
        self.campaign = campaign
        self.year = year
        self.source = source
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<DistrictCropStat crop={self.crop!r} area={self.area_ha}ha>"


class SoilUnit(Base):
    """National soil classification unit (INIA / IIAM, 1995)."""

    __tablename__ = "soil_units"

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
    properties: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )
    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="INIA/IIAM 1995",
    )
    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1995,
    )
    boundary: Mapped[Any] = mapped_column(
        Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True),
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
        code: str,
        name: str,
        description: str | None = None,
        properties: dict[str, Any] | None = None,
        source: str = "INIA/IIAM 1995",
        year: int = 1995,
        boundary: Any = None,
        id: uuid.UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id or uuid.uuid4()
        self.code = code
        self.name = name
        self.description = description
        self.properties = properties or {}
        self.source = source
        self.year = year
        self.boundary = boundary
        now = datetime.now(UTC)
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def __repr__(self) -> str:
        return f"<SoilUnit code={self.code!r} name={self.name!r}>"
