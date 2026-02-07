"""Insights service – builds full employee insight payloads with explainability."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Employee, WeeklySignal, EmployeeScore, EmployeeSkill, Team
from app.schemas import (
    EmployeeSummary, EmployeeInsights, ExplainabilityCard,
    SignalRow, OrgOverview, TeamSummary,
)
from app.scoring.scorer import compute_all_scores, detect_hidden_talent, predict_burnout
from app.scoring.bias import build_fairness_note


def _generate_recommendations(scores: list[dict], signals: list[dict]) -> list[str]:
    """Generate actionable recommendations based on scores and signals."""
    recs = []
    if not scores or not signals:
        return ["Insufficient data for recommendations. Continue collecting signals."]

    score_map = {s["score_name"]: s for s in scores}
    current = signals[0]

    # Burnout / pressure recommendations
    br = score_map.get("burnout_risk", {})
    hp_score = score_map.get("high_pressure", {})

    if br.get("score", 0) >= 60:
        recs.append("🔴 HIGH BURNOUT RISK: Prioritize a wellness check-in. Review workload immediately.")
        if current.get("meeting_hours", 0) > 15:
            recs.append("📅 Meeting overload detected. Review meeting necessity – cancel or shorten recurring meetings.")
        if current.get("after_hours_events", 0) > 4:
            recs.append("🌙 High after-hours activity. Establish boundaries and protect personal time.")
        if current.get("focus_blocks", 0) < 3:
            recs.append("🎯 Insufficient deep work time. Block 2-hour focus slots on calendar.")
    elif br.get("score", 0) >= 40:
        recs.append("⚠️ MODERATE BURNOUT RISK: Schedule a casual check-in within the next sprint.")

    # Performance degradation
    pd = score_map.get("performance_degradation", {})
    if pd.get("score", 0) >= 55:
        recs.append("📉 Performance trend declining. Identify blockers in next 1:1 – avoid blame framing.")
        if current.get("missed_deadlines", 0) >= 2:
            recs.append("🎯 Rising missed deadlines. Consider workload redistribution or dependency analysis.")

    # High potential
    pot = score_map.get("high_potential", {})
    if pot.get("score", 0) >= 60:
        recs.append("⭐ High growth potential detected. Consider stretch assignments or mentorship opportunities.")
        if current.get("learning_hours", 0) >= 3:
            recs.append("📚 Strong learning engagement. Support with conference budget or skill-building time.")
        if current.get("cross_team_ratio", 0) >= 0.4:
            recs.append("🤝 Strong cross-team connector. Consider for cross-functional initiatives.")

    # Workload redistribution
    if current.get("workload_items", 0) > 15:
        recs.append("📦 Consider redistributing tasks. Current workload significantly above team average.")

    # Collaboration
    if current.get("unique_collaborators", 0) < 4:
        recs.append("👥 Low collaboration breadth. Foster connections through pair programming or cross-team activities.")

    if not recs:
        recs.append("✅ Signals look healthy. Continue supporting current trajectory.")

    return recs


async def get_employee_insights(
    db: AsyncSession,
    employee_id: uuid.UUID,
) -> EmployeeInsights:
    """Build full insights for an employee."""
    # Fetch employee
    emp = await db.get(Employee, employee_id)
    if not emp:
        raise ValueError(f"Employee {employee_id} not found")

    # Fetch signals (newest first)
    result = await db.execute(
        select(WeeklySignal)
        .where(WeeklySignal.employee_id == employee_id)
        .order_by(WeeklySignal.week_start.desc())
        .limit(8)
    )
    signal_models = result.scalars().all()
    signals_dicts = [
        {
            "week_start": s.week_start,
            "tasks_completed": s.tasks_completed,
            "missed_deadlines": s.missed_deadlines,
            "workload_items": s.workload_items,
            "cycle_time_days": s.cycle_time_days,
            "meeting_hours": s.meeting_hours,
            "meeting_count": s.meeting_count,
            "avg_meeting_length_min": s.avg_meeting_length_min,
            "fragmentation_score": s.fragmentation_score,
            "focus_blocks": s.focus_blocks,
            "response_time_bucket": s.response_time_bucket,
            "after_hours_events": s.after_hours_events,
            "unique_collaborators": s.unique_collaborators,
            "cross_team_ratio": s.cross_team_ratio,
            "support_actions": s.support_actions,
            "learning_hours": s.learning_hours,
            "stretch_assignments": s.stretch_assignments,
            "skill_progress": s.skill_progress,
            "data_quality": s.data_quality,
        }
        for s in signal_models
    ]

    signal_rows = [SignalRow(**sd) for sd in signals_dicts]

    # Compute scores
    data_quality = signals_dicts[0].get("data_quality", 1.0) if signals_dicts else 1.0
    raw_scores = compute_all_scores(signals_dicts, data_quality)

    # Fairness note
    cohort_result = await db.execute(
        select(func.count(Employee.id))
        .where(Employee.role == emp.role, Employee.seniority == emp.seniority)
    )
    cohort_size = cohort_result.scalar() or 0

    fairness = build_fairness_note(emp.role, emp.seniority, emp.tenure_months, cohort_size)

    # Build explainability cards
    explainability_cards = [
        ExplainabilityCard(
            score_name=s["score_name"],
            score=s["score"],
            label=s["label"],
            top_contributors=s["top_contributors"],
            trend_explanation=s["trend_explanation"],
            confidence=s["confidence"],
            limitations=s["limitations"],
            fairness_warning=fairness,
        )
        for s in raw_scores
    ]

    # Recommendations
    recommendations = _generate_recommendations(raw_scores, signals_dicts)

    # Hidden talent detection
    hidden_talent = detect_hidden_talent(raw_scores, signals_dicts)

    # Predictive burnout
    predictive = predict_burnout(raw_scores, signals_dicts)

    # Skills
    skills_result = await db.execute(
        select(EmployeeSkill).where(EmployeeSkill.employee_id == employee_id)
    )
    skills = [
        {"skill_name": sk.skill_name, "proficiency": sk.proficiency, "is_growing": sk.is_growing}
        for sk in skills_result.scalars().all()
    ]

    # Build summary
    latest_score_map = {s["score_name"]: s for s in raw_scores}
    summary = EmployeeSummary(
        id=emp.id,
        name=emp.name,
        email=emp.email,
        role=emp.role,
        seniority=emp.seniority,
        tenure_months=emp.tenure_months,
        team_name=emp.team.name if emp.team else "",
        team_id=emp.team_id,
        burnout_risk=latest_score_map.get("burnout_risk", {}).get("score", 0),
        burnout_label=latest_score_map.get("burnout_risk", {}).get("label", "N/A"),
        high_potential=latest_score_map.get("high_potential", {}).get("score", 0),
        potential_label=latest_score_map.get("high_potential", {}).get("label", "N/A"),
        performance_degradation=latest_score_map.get("performance_degradation", {}).get("score", 0),
        degradation_label=latest_score_map.get("performance_degradation", {}).get("label", "N/A"),
        high_pressure=latest_score_map.get("high_pressure", {}).get("score", 0),
        pressure_label=latest_score_map.get("high_pressure", {}).get("label", "N/A"),
    )

    return EmployeeInsights(
        employee=summary,
        signals=signal_rows,
        scores=explainability_cards,
        recommendations=recommendations,
        hidden_talent=hidden_talent,
        predictive_burnout=predictive,
        skills=skills,
    )


async def get_org_overview(db: AsyncSession) -> OrgOverview:
    """Build org-level overview with distributions and alerts."""
    # Count employees and teams
    emp_count = (await db.execute(select(func.count(Employee.id)).where(Employee.is_active))).scalar() or 0
    team_count = (await db.execute(select(func.count(Team.id)))).scalar() or 0

    # Get all active employees
    result = await db.execute(select(Employee).where(Employee.is_active))
    employees = result.scalars().all()

    burnout_dist = {"Low": 0, "Medium": 0, "High": 0}
    pressure_dist = {"Low": 0, "Medium": 0, "High": 0}
    potential_dist = {"Low": 0, "Medium": 0, "High": 0}
    degradation_dist = {"Low": 0, "Medium": 0, "High": 0}
    trending_alerts = []
    team_workloads: dict[str, list[float]] = {}

    for emp in employees:
        # Get latest score
        score_result = await db.execute(
            select(EmployeeScore)
            .where(EmployeeScore.employee_id == emp.id)
            .order_by(EmployeeScore.week_start.desc())
            .limit(1)
        )
        score = score_result.scalar()

        if score:
            burnout_dist[score.burnout_label] = burnout_dist.get(score.burnout_label, 0) + 1
            pressure_dist[score.pressure_label] = pressure_dist.get(score.pressure_label, 0) + 1
            potential_dist[score.potential_label] = potential_dist.get(score.potential_label, 0) + 1
            degradation_dist[score.degradation_label] = degradation_dist.get(score.degradation_label, 0) + 1

            if score.burnout_label == "High":
                trending_alerts.append({
                    "type": "burnout_risk",
                    "employee": emp.name,
                    "team": emp.team.name if emp.team else "",
                    "score": score.burnout_risk,
                    "message": f"{emp.name} shows high burnout risk ({score.burnout_risk:.0f})",
                })

            # Collect team workloads
            signal_result = await db.execute(
                select(WeeklySignal)
                .where(WeeklySignal.employee_id == emp.id)
                .order_by(WeeklySignal.week_start.desc())
                .limit(1)
            )
            signal = signal_result.scalar()
            if signal and emp.team:
                team_name = emp.team.name
                if team_name not in team_workloads:
                    team_workloads[team_name] = []
                team_workloads[team_name].append(float(signal.workload_items))

    # Find overloaded teams
    overloaded_teams = []
    for team_name, workloads in team_workloads.items():
        avg = sum(workloads) / len(workloads) if workloads else 0
        if avg > 14:
            overloaded_teams.append({"team": team_name, "avg_workload": round(avg, 1)})

    return OrgOverview(
        total_employees=emp_count,
        total_teams=team_count,
        burnout_risk_distribution=burnout_dist,
        pressure_distribution=pressure_dist,
        potential_distribution=potential_dist,
        degradation_distribution=degradation_dist,
        trending_alerts=sorted(trending_alerts, key=lambda x: x.get("score", 0), reverse=True),
        overloaded_teams=overloaded_teams,
        collaboration_bottlenecks=[],
    )


async def get_team_summaries(db: AsyncSession) -> list[TeamSummary]:
    """Build team-level summaries."""
    result = await db.execute(select(Team))
    teams = result.scalars().all()

    summaries = []
    for team in teams:
        employees = team.employees
        active = [e for e in employees if e.is_active]

        if not active:
            continue

        burnout_scores = []
        potential_scores = []
        degradation_scores = []
        workloads = []

        for emp in active:
            score_result = await db.execute(
                select(EmployeeScore)
                .where(EmployeeScore.employee_id == emp.id)
                .order_by(EmployeeScore.week_start.desc())
                .limit(1)
            )
            score = score_result.scalar()
            if score:
                burnout_scores.append(score.burnout_risk)
                potential_scores.append(score.high_potential)
                degradation_scores.append(score.performance_degradation)

            signal_result = await db.execute(
                select(WeeklySignal)
                .where(WeeklySignal.employee_id == emp.id)
                .order_by(WeeklySignal.week_start.desc())
                .limit(1)
            )
            sig = signal_result.scalar()
            if sig:
                workloads.append(float(sig.workload_items))

        import numpy as np
        avg_b = round(float(np.mean(burnout_scores)), 1) if burnout_scores else 0
        avg_p = round(float(np.mean(potential_scores)), 1) if potential_scores else 0
        avg_d = round(float(np.mean(degradation_scores)), 1) if degradation_scores else 0
        imbalance = round(float(np.std(workloads)), 1) if len(workloads) > 1 else 0

        trend = "stable"
        if avg_b > 55:
            trend = "concerning"
        elif avg_b < 30 and avg_p > 50:
            trend = "thriving"

        summaries.append(TeamSummary(
            id=team.id,
            name=team.name,
            department=team.department,
            employee_count=len(active),
            avg_burnout_risk=avg_b,
            avg_high_potential=avg_p,
            avg_performance_degradation=avg_d,
            workload_imbalance=imbalance,
            trend=trend,
        ))

    return summaries
