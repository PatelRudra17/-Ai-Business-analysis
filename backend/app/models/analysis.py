import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    display_name: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    point: Mapped[object] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(50), default="India")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SearchGrid(Base):
    __tablename__ = "search_grids"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False)
    grid_points: Mapped[list] = mapped_column(JSON, nullable=False)  # [{lat, lng}]
    radius_meters: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    analysis_job: Mapped["AnalysisJob"] = relationship("AnalysisJob", back_populates="search_grid")


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("locations.id"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("business_categories.id"), nullable=False)
    subtype_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("business_subtypes.id"), nullable=True)

    # Status: queued | processing | completed | failed
    status: Mapped[str] = mapped_column(String(50), default="queued", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # User inputs
    radius_meters: Mapped[int] = mapped_column(Integer, default=3000)
    total_investment: Mapped[float | None] = mapped_column(Float, nullable=True)
    monthly_rent_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    average_order_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_customer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    preferred_floor_area_sqft: Mapped[float | None] = mapped_column(Float, nullable=True)
    parking_required: Mapped[bool] = mapped_column(Boolean, default=False)
    additional_inputs: Mapped[dict] = mapped_column(JSON, default=dict)

    # Workflow tracking
    n8n_workflow_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    workflow_steps: Mapped[dict] = mapped_column(JSON, default=dict)

    # Unlock state
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)
    payment_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    search_grid: Mapped["SearchGrid | None"] = relationship("SearchGrid", back_populates="analysis_job")
    location: Mapped["Location"] = relationship("Location")
