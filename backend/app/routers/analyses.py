import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from geoalchemy2.elements import WKTElement
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user, get_optional_user
from app.models.analysis import AnalysisJob, Location
from app.models.category import BusinessCategory, BusinessSubtype
from app.models.financial import FinancialScenario
from app.models.report import Report
from app.models.scoring import ScoreVersion
from app.models.user import User
from app.schemas.analysis import (
    AnalysisCreate, AnalysisJobOut, AnalysisStatusOut,
    FinancialScenarioOut, ReportOut, ScoreOut,
)
from app.workers.analysis_worker import run_analysis

router = APIRouter()


@router.post("", status_code=202)
async def create_analysis(
    body: AnalysisCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    category = await db.scalar(select(BusinessCategory).where(BusinessCategory.slug == body.business_type))
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{body.business_type}' not found")

    subtype = None
    if body.business_subtype:
        subtype = await db.scalar(
            select(BusinessSubtype).where(
                BusinessSubtype.slug == body.business_subtype,
                BusinessSubtype.category_id == category.id,
            )
        )

    point = WKTElement(f"POINT({body.longitude} {body.latitude})", srid=4326)
    location = Location(
        display_name=body.location_text,
        latitude=body.latitude,
        longitude=body.longitude,
        point=point,
        organization_id=user.organization_id,
    )
    db.add(location)
    await db.flush()

    job = AnalysisJob(
        user_id=user.id,
        organization_id=user.organization_id,
        location_id=location.id,
        category_id=category.id,
        subtype_id=subtype.id if subtype else None,
        radius_meters=body.radius_meters,
        total_investment=body.total_investment,
        monthly_rent_limit=body.monthly_rent_limit,
        average_order_value=body.average_order_value,
        target_customer=body.target_customer,
        preferred_floor_area_sqft=body.preferred_floor_area_sqft,
        parking_required=body.parking_required,
        status="queued",
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    # Run analysis pipeline in background
    background_tasks.add_task(run_analysis, job.id)

    return {"analysis_id": str(job.id), "status": "queued"}


@router.get("", response_model=list[AnalysisJobOut])
async def list_analyses(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rows = await db.scalars(
        select(AnalysisJob)
        .where(AnalysisJob.user_id == user.id)
        .order_by(AnalysisJob.created_at.desc())
        .limit(50)
    )
    return rows.all()


@router.get("/{analysis_id}", response_model=AnalysisJobOut)
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = await db.get(AnalysisJob, analysis_id)
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return job


@router.get("/{analysis_id}/status", response_model=AnalysisStatusOut)
async def get_status(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_optional_user),
):
    job = await db.get(AnalysisJob, analysis_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return AnalysisStatusOut(
        analysis_id=job.id,
        status=job.status,
        workflow_steps=job.workflow_steps,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/{analysis_id}/report", response_model=ReportOut)
async def get_report(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_optional_user),
):
    job = await db.get(AnalysisJob, analysis_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if job.status != "completed":
        raise HTTPException(status_code=202, detail=f"Report not ready — status: {job.status}")

    report = await db.scalar(select(Report).where(Report.analysis_job_id == analysis_id))
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet")

    # Lock non-free sections for unpaid analyses
    if not job.is_paid:
        report.competitor_landscape = {
            **report.competitor_landscape,
            "competitors": report.competitor_landscape.get("competitors", [])[:3],
            "locked": True,
        }
        report.gap_finder = {"locked": True, "count": report.gap_finder.get("count", 0)}
        report.marketing_strategy = {"locked": True}
        report.launch_plan = []
    return report


@router.get("/{analysis_id}/scores", response_model=ScoreOut)
async def get_scores(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_optional_user),
):
    sv = await db.scalar(select(ScoreVersion).where(ScoreVersion.analysis_job_id == analysis_id))
    if not sv:
        raise HTTPException(status_code=404, detail="Scores not yet available")
    return sv


@router.get("/{analysis_id}/financials", response_model=list[FinancialScenarioOut])
async def get_financials(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = await db.get(AnalysisJob, analysis_id)
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if not job.is_paid:
        raise HTTPException(status_code=402, detail="Unlock the report to view financial scenarios")
    rows = await db.scalars(select(FinancialScenario).where(FinancialScenario.analysis_job_id == analysis_id))
    return rows.all()
