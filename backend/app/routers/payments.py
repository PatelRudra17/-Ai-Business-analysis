import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.analysis import AnalysisJob
from app.models.billing import Payment
from app.models.user import User
from app.services.razorpay_service import create_order, verify_payment_signature

router = APIRouter()


class CreateOrderRequest(BaseModel):
    analysis_id: uuid.UUID
    product: str = "single_report"


class VerifyPaymentRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str
    analysis_id: uuid.UUID


@router.post("/orders")
async def create_payment_order(
    body: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    job = await db.get(AnalysisJob, body.analysis_id)
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Analysis not found")
    if job.is_paid:
        raise HTTPException(status_code=400, detail="This analysis is already unlocked")

    order = create_order(body.product, str(body.analysis_id), user.email)

    payment = Payment(
        user_id=user.id,
        analysis_job_id=body.analysis_id,
        razorpay_order_id=order["order_id"],
        amount_paise=order["amount_paise"],
        product=body.product,
        status="pending",
    )
    db.add(payment)
    await db.commit()
    return order


@router.post("/verify")
async def verify_payment(
    body: VerifyPaymentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_payment_signature(body.order_id, body.payment_id, body.signature):
        raise HTTPException(status_code=400, detail="Payment verification failed")

    job = await db.get(AnalysisJob, body.analysis_id)
    if not job or job.user_id != user.id:
        raise HTTPException(status_code=404, detail="Analysis not found")

    job.is_paid = True
    job.payment_id = body.payment_id
    await db.commit()
    return {"unlocked": True, "analysis_id": str(body.analysis_id)}
