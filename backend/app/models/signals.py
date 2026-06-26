import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AreaSignal(Base):
    """Nearby demand signals grouped by distance ring."""
    __tablename__ = "area_signals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "college", "office"
    place_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    distance_meters: Mapped[float] = mapped_column(Float, nullable=False)
    distance_ring: Mapped[str] = mapped_column(String(20), nullable=False)  # "0-1km", "1-3km", "3-5km"
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="google_places")
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DemographicRegion(Base):
    __tablename__ = "demographic_regions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False)
    region_name: Mapped[str] = mapped_column(String(255), nullable=False)
    region_type: Mapped[str] = mapped_column(String(50), nullable=False)  # ward | town | district
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    household_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(255), default="Census of India")
    proxies: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DevelopmentProject(Base):
    __tablename__ = "development_projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name: Mapped[str] = mapped_column(String(500), nullable=False)
    project_type: Mapped[str] = mapped_column(String(100), nullable=False)  # residential | commercial | mixed
    developer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    units: Mapped[int | None] = mapped_column(Integer, nullable=True)
    expected_completion: Mapped[str | None] = mapped_column(String(50), nullable=True)
    rera_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str] = mapped_column(String(255), default="RERA Portal")
    source_version: Mapped[str] = mapped_column(String(50), default="v1")
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
