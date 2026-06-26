import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.analysis import AnalysisJob
from app.models.scoring import ScoreVersion
from sqlalchemy import select

router = APIRouter()


class ComparisonCreate(BaseModel):
    analysis_id_a: uuid.UUID
    analysis_id_b: uuid.UUID


class ComparisonOut(BaseModel):
    analysis_a: dict
    analysis_b: dict
    winner: str  # "a" | "b" | "tie"
    recommendation: str
    score_diff: float


@router.post("", response_model=ComparisonOut)
async def compare_locations(body: ComparisonCreate, db: AsyncSession = Depends(get_db)):
    job_a = await db.get(AnalysisJob, body.analysis_id_a)
    job_b = await db.get(AnalysisJob, body.analysis_id_b)

    if not job_a or not job_b:
        raise HTTPException(status_code=404, detail="One or both analyses not found")
    if job_a.category_id != job_b.category_id:
        raise HTTPException(status_code=400, detail="Both analyses must be for the same business category")
    if job_a.status != "completed" or job_b.status != "completed":
        raise HTTPException(status_code=202, detail="Both analyses must be completed before comparison")

    score_a = await db.scalar(select(ScoreVersion).where(ScoreVersion.analysis_job_id == job_a.id))
    score_b = await db.scalar(select(ScoreVersion).where(ScoreVersion.analysis_job_id == job_b.id))

    if not score_a or not score_b:
        raise HTTPException(status_code=404, detail="Scores not yet available for comparison")

    diff = score_a.final_opportunity_score - score_b.final_opportunity_score
    if abs(diff) < 5:
        winner = "tie"
        recommendation = "Both locations are closely matched. On-ground validation is recommended before deciding."
    elif diff > 0:
        winner = "a"
        recommendation = f"Location A scores {diff:.1f} points higher. Consider it as the primary candidate."
    else:
        winner = "b"
        recommendation = f"Location B scores {abs(diff):.1f} points higher. Consider it as the primary candidate."

    return ComparisonOut(
        analysis_a={
            "analysis_id": str(job_a.id),
            "opportunity_score": score_a.final_opportunity_score,
            "risk_score": score_a.risk_score,
            "confidence": score_a.confidence_score,
            "decision": score_a.decision,
        },
        analysis_b={
            "analysis_id": str(job_b.id),
            "opportunity_score": score_b.final_opportunity_score,
            "risk_score": score_b.risk_score,
            "confidence": score_b.confidence_score,
            "decision": score_b.decision,
        },
        winner=winner,
        recommendation=recommendation,
        score_diff=round(diff, 2),
    )
