"""Org overview endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas import OrgOverview
from app.services.insights import get_org_overview

router = APIRouter(tags=["org"])


@router.get("/org/overview", response_model=OrgOverview)
async def org_overview(db: AsyncSession = Depends(get_db)):
    return await get_org_overview(db)
