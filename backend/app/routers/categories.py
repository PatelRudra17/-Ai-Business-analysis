import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.category import BusinessCategory, BusinessSubtype

router = APIRouter()


class CategoryOut(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    description: str | None
    icon: str | None
    model_config = {"from_attributes": True}


class SubtypeOut(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    description: str | None
    model_config = {"from_attributes": True}


@router.get("", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(
        select(BusinessCategory)
        .where(BusinessCategory.is_active == True)
        .order_by(BusinessCategory.display_order)
    )
    return rows.all()


@router.get("/{category_id}/subtypes", response_model=list[SubtypeOut])
async def list_subtypes(category_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    category = await db.get(BusinessCategory, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    rows = await db.scalars(
        select(BusinessSubtype)
        .where(
            BusinessSubtype.category_id == category_id,
            BusinessSubtype.is_active == True,
        )
    )
    return rows.all()
