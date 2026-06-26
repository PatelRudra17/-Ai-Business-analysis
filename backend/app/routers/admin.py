"""Admin dashboard endpoints — restricted to admin role."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import require_role
from app.models.analysis import AnalysisJob
from app.models.audit import AIRun, ApiUsage
from app.models.billing import Payment
from app.models.user import User

router = APIRouter()


@router.get("/stats")
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    since_30d = datetime.now(timezone.utc) - timedelta(days=30)

    total_users = await db.scalar(select(func.count()).select_from(User))
    total_analyses = await db.scalar(select(func.count()).select_from(AnalysisJob))
    completed = await db.scalar(select(func.count()).select_from(AnalysisJob).where(AnalysisJob.status == "completed"))
    failed = await db.scalar(select(func.count()).select_from(AnalysisJob).where(AnalysisJob.status == "failed"))
    paid_count = await db.scalar(select(func.count()).select_from(AnalysisJob).where(AnalysisJob.is_paid == True))

    total_revenue_paise = await db.scalar(
        select(func.sum(Payment.amount_paise)).where(Payment.status == "paid")
    ) or 0

    ai_tokens_in = await db.scalar(select(func.sum(AIRun.input_tokens)).where(AIRun.created_at >= since_30d)) or 0
    ai_tokens_out = await db.scalar(select(func.sum(AIRun.output_tokens)).where(AIRun.created_at >= since_30d)) or 0
    api_calls = await db.scalar(select(func.sum(ApiUsage.request_count)).where(ApiUsage.created_at >= since_30d)) or 0

    return {
        "users": {"total": total_users},
        "analyses": {
            "total": total_analyses,
            "completed": completed,
            "failed": failed,
            "paid": paid_count,
            "conversion_rate_pct": round((paid_count / completed * 100) if completed else 0, 1),
        },
        "revenue": {
            "total_inr": round(total_revenue_paise / 100, 2),
        },
        "ai_cost_30d": {
            "input_tokens": ai_tokens_in,
            "output_tokens": ai_tokens_out,
            "estimated_usd": round((ai_tokens_in * 0.25 + ai_tokens_out * 1.25) / 1_000_000, 2),
        },
        "api_calls_30d": api_calls,
    }


@router.get("/analyses")
async def admin_analyses(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
    status: str | None = None,
    limit: int = 50,
):
    q = select(AnalysisJob).order_by(AnalysisJob.created_at.desc()).limit(limit)
    if status:
        q = q.where(AnalysisJob.status == status)
    rows = await db.scalars(q)
    jobs = rows.all()
    return [{"id": str(j.id), "status": j.status, "is_paid": j.is_paid, "created_at": j.created_at} for j in jobs]


@router.get("/users")
async def admin_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    rows = await db.scalars(select(User).order_by(User.created_at.desc()).limit(100))
    users = rows.all()
    return [{"id": str(u.id), "email": u.email, "full_name": u.full_name, "role": u.role, "created_at": u.created_at} for u in users]
