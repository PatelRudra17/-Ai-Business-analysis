import hashlib
import hmac
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.analysis import AnalysisJob

router = APIRouter()


def verify_n8n_signature(raw_body: bytes, signature: str) -> bool:
    expected = hmac.new(settings.N8N_WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


class N8NJobCompleted(BaseModel):
    analysis_id: uuid.UUID
    status: str  # completed | failed
    workflow_steps: dict = {}
    error_message: str | None = None


@router.post("/n8n/job-completed")
async def n8n_job_completed(
    request: Request,
    body: N8NJobCompleted,
    x_webhook_signature: str = Header(default=""),
    db: AsyncSession = Depends(get_db),
):
    raw = await request.body()
    if settings.ENVIRONMENT != "development" and not verify_n8n_signature(raw, x_webhook_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    job = await db.get(AnalysisJob, body.analysis_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")

    job.status = body.status
    job.workflow_steps = body.workflow_steps
    job.error_message = body.error_message
    if body.status == "completed":
        job.completed_at = datetime.now(timezone.utc)

    return {"received": True}


class RazorpayWebhookBody(BaseModel):
    event: str
    payload: dict


@router.post("/razorpay")
async def razorpay_webhook(body: RazorpayWebhookBody, db: AsyncSession = Depends(get_db)):
    if body.event == "payment.captured":
        payment_entity = body.payload.get("payment", {}).get("entity", {})
        notes = payment_entity.get("notes", {})
        analysis_id = notes.get("analysis_id")
        if analysis_id:
            job = await db.get(AnalysisJob, uuid.UUID(analysis_id))
            if job:
                job.is_paid = True
                job.payment_id = payment_entity.get("id")
    return {"received": True}
