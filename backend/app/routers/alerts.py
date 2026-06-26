import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.billing import AlertSubscription

router = APIRouter()


class AlertSubscriptionCreate(BaseModel):
    analysis_job_id: uuid.UUID
    alert_types: list[str] = ["new_competitor", "rating_change", "new_development"]
    channels: list[str] = ["email"]


class AlertSubscriptionOut(BaseModel):
    id: uuid.UUID
    analysis_job_id: uuid.UUID
    is_active: bool
    alert_types: list
    channels: list
    model_config = {"from_attributes": True}


@router.post("", response_model=AlertSubscriptionOut, status_code=201)
async def create_alert(body: AlertSubscriptionCreate, db: AsyncSession = Depends(get_db)):
    sub = AlertSubscription(
        user_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),  # TODO: auth
        analysis_job_id=body.analysis_job_id,
        alert_types=body.alert_types,
        channels=body.channels,
    )
    db.add(sub)
    await db.flush()
    await db.refresh(sub)
    return sub


@router.get("", response_model=list[AlertSubscriptionOut])
async def list_alerts(db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(
        select(AlertSubscription).where(
            AlertSubscription.user_id == uuid.UUID("00000000-0000-0000-0000-000000000001"),
            AlertSubscription.is_active == True,
        )
    )
    return rows.all()


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(alert_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    sub = await db.get(AlertSubscription, alert_id)
    if not sub:
        raise HTTPException(status_code=404, detail="Alert not found")
    sub.is_active = False
