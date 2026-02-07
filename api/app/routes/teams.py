"""Teams endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas import TeamSummary
from app.services.insights import get_team_summaries

router = APIRouter(tags=["teams"])


@router.get("/teams", response_model=list[TeamSummary])
async def list_teams(db: AsyncSession = Depends(get_db)):
    return await get_team_summaries(db)
