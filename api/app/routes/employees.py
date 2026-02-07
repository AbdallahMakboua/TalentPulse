"""Employees endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Employee, EmployeeScore, WeeklySignal, EmployeeSkill
from app.schemas import EmployeeSummary, EmployeeInsights, QuestionsResponse, ReviewDraftResponse
from app.services.insights import get_employee_insights
from app.services.questions import generate_questions
from app.services.reviews import generate_review

router = APIRouter(tags=["employees"])


@router.get("/employees", response_model=list[EmployeeSummary])
async def list_employees(
    risk_filter: str | None = Query(None, description="Filter: High, Medium, Low"),
    team: str | None = Query(None, description="Filter by team name"),
    db: AsyncSession = Depends(get_db),
):
    """List all employees with search and risk filters."""
    query = select(Employee).where(Employee.is_active)

    result = await db.execute(query)
    employees = result.scalars().all()

    summaries = []
    for emp in employees:
        # Filter by team
        if team and emp.team and emp.team.name != team:
            continue

        # Get latest score
        score_result = await db.execute(
            select(EmployeeScore)
            .where(EmployeeScore.employee_id == emp.id)
            .order_by(EmployeeScore.week_start.desc())
            .limit(1)
        )
        score = score_result.scalar()

        s = EmployeeSummary(
            id=emp.id,
            name=emp.name,
            email=emp.email,
            role=emp.role,
            seniority=emp.seniority,
            tenure_months=emp.tenure_months,
            team_name=emp.team.name if emp.team else "",
            team_id=emp.team_id,
            burnout_risk=score.burnout_risk if score else 0,
            burnout_label=score.burnout_label if score else "N/A",
            high_potential=score.high_potential if score else 0,
            potential_label=score.potential_label if score else "N/A",
            performance_degradation=score.performance_degradation if score else 0,
            degradation_label=score.degradation_label if score else "N/A",
            high_pressure=score.high_pressure if score else 0,
            pressure_label=score.pressure_label if score else "N/A",
        )

        # Apply risk filter
        if risk_filter:
            if risk_filter != s.burnout_label:
                continue

        summaries.append(s)

    return summaries


@router.get("/employees/{employee_id}/insights", response_model=EmployeeInsights)
async def employee_insights(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get full explainable insights for an employee."""
    try:
        return await get_employee_insights(db, employee_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/employees/{employee_id}/questions", response_model=QuestionsResponse)
async def employee_questions(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate 1:1 coaching agenda (Manager Coaching Copilot)."""
    try:
        return await generate_questions(db, employee_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/employees/{employee_id}/review-draft", response_model=ReviewDraftResponse)
async def employee_review_draft(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate dynamic performance review draft."""
    try:
        return await generate_review(db, employee_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/employees/{employee_id}/data")
async def delete_employee_data(
    employee_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete all data for an employee (data minimization / GDPR)."""
    emp = await db.get(Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Delete all related data
    await db.execute(delete(WeeklySignal).where(WeeklySignal.employee_id == employee_id))
    await db.execute(delete(EmployeeScore).where(EmployeeScore.employee_id == employee_id))
    await db.execute(delete(EmployeeSkill).where(EmployeeSkill.employee_id == employee_id))
    emp.is_active = False
    await db.commit()

    return {
        "status": "deleted",
        "employee_id": str(employee_id),
        "message": "All signal data, scores, and skills deleted. Employee deactivated.",
    }
