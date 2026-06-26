import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ScoreVersion(Base):
    """Top-level opportunity and risk scores for an analysis."""
    __tablename__ = "score_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False, unique=True)
    formula_version: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "cafe-opportunity-v1.0"

    # Raw + penalized
    raw_opportunity_score: Mapped[float] = mapped_column(Float, nullable=False)
    penalties: Mapped[float] = mapped_column(Float, default=0)
    final_opportunity_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Decision
    decision: Mapped[str] = mapped_column(String(100), nullable=False)
    decision_summary: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    best_gap: Mapped[str | None] = mapped_column(String(500), nullable=True)
    main_risk: Mapped[str | None] = mapped_column(String(500), nullable=True)
    next_action: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    components: Mapped[list["ScoreComponent"]] = relationship("ScoreComponent", back_populates="score_version")


class ScoreComponent(Base):
    """Individual component score with supporting evidence."""
    __tablename__ = "score_components"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    score_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("score_versions.id"), nullable=False)
    component_name: Mapped[str] = mapped_column(String(100), nullable=False)  # demand_potential, competition_gap, etc.
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    raw_value: Mapped[float] = mapped_column(Float, nullable=False)
    weighted_value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.8)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    score_version: Mapped["ScoreVersion"] = relationship("ScoreVersion", back_populates="components")
