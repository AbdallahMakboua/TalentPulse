"""Settings endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import AppSettings
from app.schemas import SettingsIn, SettingsOut

router = APIRouter(tags=["settings"])


async def _get_or_create(db: AsyncSession) -> AppSettings:
    result = await db.execute(select(AppSettings).where(AppSettings.id == 1))
    settings = result.scalar()
    if not settings:
        settings = AppSettings(id=1)
        db.add(settings)
        await db.flush()
    return settings


@router.get("/settings", response_model=SettingsOut)
async def get_settings(db: AsyncSession = Depends(get_db)):
    s = await _get_or_create(db)
    return SettingsOut.model_validate(s)


@router.post("/settings", response_model=SettingsOut)
async def update_settings(body: SettingsIn, db: AsyncSession = Depends(get_db)):
    s = await _get_or_create(db)

    for field, value in body.model_dump(exclude_none=True).items():
        setattr(s, field, value)

    await db.commit()
    await db.refresh(s)
    return SettingsOut.model_validate(s)
