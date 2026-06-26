import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Place(Base):
    """A competitor or nearby place of interest, keyed by Google Place ID."""
    __tablename__ = "places"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    place_type: Mapped[str] = mapped_column(String(100), nullable=False)  # competitor | signal
    category_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    point: Mapped[object] = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    address: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    google_types: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    snapshots: Mapped[list["PlaceSnapshot"]] = relationship("PlaceSnapshot", back_populates="place", order_by="PlaceSnapshot.collected_at.desc()")
    review_samples: Mapped[list["ReviewSample"]] = relationship("ReviewSample", back_populates="place")


class PlaceSnapshot(Base):
    """Point-in-time snapshot of a place's rating and hours."""
    __tablename__ = "place_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("places.id"), nullable=False)
    analysis_job_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    review_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_level: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-4
    is_open_now: Mapped[bool | None] = mapped_column(nullable=True)
    opening_hours: Mapped[dict] = mapped_column(JSON, default=dict)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="google_places")
    source_version: Mapped[str] = mapped_column(String(50), default="v1")
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    place: Mapped["Place"] = relationship("Place", back_populates="snapshots")


class ReviewSample(Base):
    __tablename__ = "review_samples"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("places.id"), nullable=False)
    analysis_job_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    source: Mapped[str] = mapped_column(String(100), default="google_places")
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    place: Mapped["Place"] = relationship("Place", back_populates="review_samples")
    themes: Mapped[list["ReviewTheme"]] = relationship("ReviewTheme", back_populates="review_sample")


class ReviewTheme(Base):
    """AI-extracted theme from a review sample."""
    __tablename__ = "review_themes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_sample_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("review_samples.id"), nullable=False)
    analysis_job_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "waiting_time"
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)  # positive | negative | neutral
    severity: Mapped[int] = mapped_column(Integer, default=3)  # 1-5
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.8)
    extraction_version: Mapped[str] = mapped_column(String(50), default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    review_sample: Mapped["ReviewSample"] = relationship("ReviewSample", back_populates="themes")
