import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AnalysisCreate(BaseModel):
    business_type: str
    business_subtype: str | None = None
    location_text: str
    latitude: float
    longitude: float
    radius_meters: int = Field(default=3000, ge=500, le=10000)
    total_investment: float | None = None
    monthly_rent_limit: float | None = None
    average_order_value: float | None = None
    target_customer: str | None = None
    preferred_floor_area_sqft: float | None = None
    parking_required: bool = False


class AnalysisJobOut(BaseModel):
    id: uuid.UUID
    status: str
    category_id: uuid.UUID
    location_id: uuid.UUID
    radius_meters: int
    is_paid: bool
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class AnalysisStatusOut(BaseModel):
    analysis_id: uuid.UUID
    status: str
    workflow_steps: dict
    created_at: datetime
    updated_at: datetime


class LocationOut(BaseModel):
    id: uuid.UUID
    display_name: str
    latitude: float
    longitude: float
    city: str | None
    state: str | None

    model_config = {"from_attributes": True}


class ScoreOut(BaseModel):
    final_opportunity_score: float
    risk_score: float
    confidence_score: float
    decision: str
    decision_summary: str | None
    best_gap: str | None
    main_risk: str | None
    next_action: str | None

    model_config = {"from_attributes": True}


class CompetitorOut(BaseModel):
    place_id: str
    name: str
    latitude: float
    longitude: float
    address: str | None
    rating: float | None
    review_count: int | None
    price_level: int | None
    distance_meters: float | None = None

    model_config = {"from_attributes": True}


class GapOut(BaseModel):
    gap_type: str
    opportunity_score: float
    confidence: float
    supporting_signals: list[str]
    limitations: list[str]


class FinancialScenarioOut(BaseModel):
    scenario_type: str
    monthly_revenue: float
    monthly_costs: float
    monthly_profit: float
    gross_margin_pct: float
    break_even_months: float
    break_even_customers_per_day: float | None

    model_config = {"from_attributes": True}


class ReportOut(BaseModel):
    id: uuid.UUID
    analysis_job_id: uuid.UUID
    executive_summary: dict
    competitor_landscape: dict
    demand_indicators: dict
    gap_finder: dict
    micro_zones: list
    marketing_strategy: dict
    launch_plan: list
    limitations: list
    data_sources: list
    is_free_preview: bool
    pdf_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
