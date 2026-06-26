import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class BusinessCategory(Base):
    __tablename__ = "business_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    subtypes: Mapped[list["BusinessSubtype"]] = relationship("BusinessSubtype", back_populates="category")
    configurations: Mapped[list["BusinessConfiguration"]] = relationship("BusinessConfiguration", back_populates="category")


class BusinessSubtype(Base):
    __tablename__ = "business_subtypes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("business_categories.id"), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    category: Mapped["BusinessCategory"] = relationship("BusinessCategory", back_populates="subtypes")


class BusinessConfiguration(Base):
    """Category-specific analysis configuration — drives all analysis workflows."""
    __tablename__ = "business_configurations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("business_categories.id"), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "cafe-v1"
    competitor_queries: Mapped[list] = mapped_column(JSON, default=list)
    positive_signals: Mapped[list] = mapped_column(JSON, default=list)
    negative_signals: Mapped[list] = mapped_column(JSON, default=list)
    review_taxonomy: Mapped[list] = mapped_column(JSON, default=list)
    scoring_weights: Mapped[dict] = mapped_column(JSON, default=dict)
    financial_model: Mapped[str] = mapped_column(String(100), nullable=False)
    scoring_model: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category: Mapped["BusinessCategory"] = relationship("BusinessCategory", back_populates="configurations")
