"""Sync endpoint – triggers signal ingestion and scoring."""

from __future__ import annotations

import uuid
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Employee, Team, WeeklySignal, EmployeeScore, EmployeeSkill
from app.schemas import SyncResponse
from app.signals.generate_demo import (
    DEMO_EMPLOYEES, generate_weekly_signals, generate_skills, get_demo_week_start,
)
from app.scoring.scorer import compute_all_scores
from app.scoring.bias import build_fairness_note

router = APIRouter(tags=["sync"])


@router.post("/sync/run", response_model=SyncResponse)
async def run_sync(db: AsyncSession = Depends(get_db)):
    """Run full sync pipeline: generate/ingest signals + compute scores."""
    employees_processed = 0
    weeks_generated = 0
    scores_computed = 0

    # ── Step 1: Ensure demo teams and employees exist ───────────
    team_cache: dict[str, uuid.UUID] = {}

    for de in DEMO_EMPLOYEES:
        # Upsert team
        if de.team not in team_cache:
            result = await db.execute(select(Team).where(Team.name == de.team))
            team = result.scalar()
            if not team:
                team = Team(name=de.team, department=de.department)
                db.add(team)
                await db.flush()
            team_cache[de.team] = team.id

        # Upsert employee
        result = await db.execute(select(Employee).where(Employee.email == de.email))
        emp = result.scalar()
        if not emp:
            emp = Employee(
                name=de.name,
                email=de.email,
                role=de.role,
                seniority=de.seniority,
                tenure_months=de.tenure_months,
                team_id=team_cache[de.team],
            )
            db.add(emp)
            await db.flush()

        # ── Step 2: Generate weekly signals ─────────────────────
        seed = hash(de.email) % 10000
        weekly_data = generate_weekly_signals(de.archetype, num_weeks=8, seed=seed)

        for i, week_data in enumerate(weekly_data):
            week_start = get_demo_week_start(weeks_ago=7 - i)

            # Check if exists
            existing = await db.execute(
                select(WeeklySignal).where(
                    WeeklySignal.employee_id == emp.id,
                    WeeklySignal.week_start == week_start,
                )
            )
            if existing.scalar():
                continue

            signal = WeeklySignal(
                employee_id=emp.id,
                week_start=week_start,
                tasks_completed=week_data["tasks_completed"],
                missed_deadlines=week_data["missed_deadlines"],
                workload_items=week_data["workload_items"],
                cycle_time_days=week_data["cycle_time_days"],
                meeting_hours=week_data["meeting_hours"],
                meeting_count=week_data["meeting_count"],
                avg_meeting_length_min=week_data["avg_meeting_length_min"],
                fragmentation_score=week_data["fragmentation_score"],
                focus_blocks=week_data["focus_blocks"],
                response_time_bucket=week_data["response_time_bucket"],
                after_hours_events=week_data["after_hours_events"],
                unique_collaborators=week_data["unique_collaborators"],
                cross_team_ratio=week_data["cross_team_ratio"],
                support_actions=week_data["support_actions"],
                learning_hours=week_data["learning_hours"],
                stretch_assignments=week_data["stretch_assignments"],
                skill_progress=week_data["skill_progress"],
                data_quality=week_data["data_quality"],
                source="demo",
            )
            db.add(signal)
            weeks_generated += 1

        # ── Step 3: Generate skills ─────────────────────────────
        existing_skills = await db.execute(
            select(EmployeeSkill).where(EmployeeSkill.employee_id == emp.id)
        )
        if not existing_skills.scalars().all():
            for skill_data in generate_skills(de.role, seed=seed):
                db.add(EmployeeSkill(
                    employee_id=emp.id,
                    skill_name=skill_data["skill_name"],
                    proficiency=skill_data["proficiency"],
                    is_growing=skill_data["is_growing"],
                ))

        employees_processed += 1

    await db.commit()

    # ── Step 4: Compute scores for all employees ────────────────
    result = await db.execute(select(Employee).where(Employee.is_active))
    all_employees = result.scalars().all()

    for emp in all_employees:
        # Get signals newest first
        sig_result = await db.execute(
            select(WeeklySignal)
            .where(WeeklySignal.employee_id == emp.id)
            .order_by(WeeklySignal.week_start.desc())
            .limit(8)
        )
        signal_models = sig_result.scalars().all()
        if not signal_models:
            continue

        signals_dicts = [
            {
                "tasks_completed": s.tasks_completed,
                "missed_deadlines": s.missed_deadlines,
                "workload_items": s.workload_items,
                "cycle_time_days": s.cycle_time_days,
                "meeting_hours": s.meeting_hours,
                "meeting_count": s.meeting_count,
                "fragmentation_score": s.fragmentation_score,
                "focus_blocks": s.focus_blocks,
                "after_hours_events": s.after_hours_events,
                "unique_collaborators": s.unique_collaborators,
                "cross_team_ratio": s.cross_team_ratio,
                "support_actions": s.support_actions,
                "learning_hours": s.learning_hours,
                "stretch_assignments": s.stretch_assignments,
                "skill_progress": s.skill_progress,
            }
            for s in signal_models
        ]

        data_quality = signal_models[0].data_quality
        score_results = compute_all_scores(signals_dicts, data_quality)
        week_start = signal_models[0].week_start

        # Check if score exists
        existing_score = await db.execute(
            select(EmployeeScore).where(
                EmployeeScore.employee_id == emp.id,
                EmployeeScore.week_start == week_start,
            )
        )
        if existing_score.scalar():
            continue

        score_map = {s["score_name"]: s for s in score_results}
        fairness = build_fairness_note(emp.role, emp.seniority, emp.tenure_months, 5)

        db.add(EmployeeScore(
            employee_id=emp.id,
            week_start=week_start,
            burnout_risk=score_map.get("burnout_risk", {}).get("score", 0),
            high_pressure=score_map.get("high_pressure", {}).get("score", 0),
            high_potential=score_map.get("high_potential", {}).get("score", 0),
            performance_degradation=score_map.get("performance_degradation", {}).get("score", 0),
            burnout_label=score_map.get("burnout_risk", {}).get("label", "Low"),
            pressure_label=score_map.get("high_pressure", {}).get("label", "Low"),
            potential_label=score_map.get("high_potential", {}).get("label", "Low"),
            degradation_label=score_map.get("performance_degradation", {}).get("label", "Low"),
            burnout_explanation=score_map.get("burnout_risk", {}),
            pressure_explanation=score_map.get("high_pressure", {}),
            potential_explanation=score_map.get("high_potential", {}),
            degradation_explanation=score_map.get("performance_degradation", {}),
            confidence=score_map.get("burnout_risk", {}).get("confidence", 0.5),
            limitations=score_map.get("burnout_risk", {}).get("limitations", ""),
            cohort_size=5,
            fairness_warning=fairness,
        ))
        scores_computed += 1

    await db.commit()

    return SyncResponse(
        status="completed",
        employees_processed=employees_processed,
        weeks_generated=weeks_generated,
        scores_computed=scores_computed,
        message=f"Synced {employees_processed} employees, {weeks_generated} signal weeks, {scores_computed} scores.",
    )
