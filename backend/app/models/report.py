import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False, unique=True)

    # Structured content (JSON)
    executive_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    competitor_landscape: Mapped[dict] = mapped_column(JSON, default=dict)
    demand_indicators: Mapped[dict] = mapped_column(JSON, default=dict)
    gap_finder: Mapped[dict] = mapped_column(JSON, default=dict)
    micro_zones: Mapped[list] = mapped_column(JSON, default=list)
    marketing_strategy: Mapped[dict] = mapped_column(JSON, default=dict)
    launch_plan: Mapped[list] = mapped_column(JSON, default=list)
    limitations: Mapped[list] = mapped_column(JSON, default=list)
    data_sources: Mapped[list] = mapped_column(JSON, default=list)

    # AI-generated narrative
    narrative_html: Mapped[str | None] = mapped_column(Text, nullable=True)

    # PDF
    pdf_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    pdf_generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Versioning
    report_version: Mapped[str] = mapped_column(String(50), default="v1")
    prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    is_free_preview: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    claims: Mapped[list["ReportClaim"]] = relationship("ReportClaim", back_populates="report")


class ReportClaim(Base):
    """Claim-checker output — ensures AI report doesn't make unsupported statements."""
    __tablename__ = "report_claims"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("reports.id"), nullable=False)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_supported: Mapped[bool] = mapped_column(Boolean, nullable=False)
    supporting_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    action_taken: Mapped[str | None] = mapped_column(String(100), nullable=True)  # kept | removed | qualified
    checker_version: Mapped[str] = mapped_column(String(50), default="v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    report: Mapped["Report"] = relationship("Report", back_populates="claims")
