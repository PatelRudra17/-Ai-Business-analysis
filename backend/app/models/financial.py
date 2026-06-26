import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Assumption(Base):
    """User-confirmed or benchmark-filled financial assumption."""
    __tablename__ = "assumptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)  # user_input | benchmark
    benchmark_record_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class FinancialScenario(Base):
    """Conservative / expected / optimistic revenue scenarios."""
    __tablename__ = "financial_scenarios"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False)
    scenario_type: Mapped[str] = mapped_column(String(50), nullable=False)  # conservative | expected | optimistic

    # Monthly financials
    monthly_revenue: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_costs: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_profit: Mapped[float] = mapped_column(Float, nullable=False)
    gross_margin_pct: Mapped[float] = mapped_column(Float, nullable=False)

    # Break-even
    break_even_months: Mapped[float] = mapped_column(Float, nullable=False)
    break_even_customers_per_day: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Sensitivity
    sensitivity: Mapped[dict] = mapped_column(JSON, default=dict)

    # Assumptions used
    assumptions_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
