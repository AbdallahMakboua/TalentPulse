"""Dynamic performance review generator – Ollama-enhanced with template fallback.

One-click summary for last 4 weeks: highlights, growth, risks, suggested goals.
"""

from __future__ import annotations

import json
import uuid
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Employee, WeeklySignal, EmployeeScore
from app.schemas import ReviewDraftResponse
from app.scoring.scorer import compute_all_scores
from app.signals.compute import compute_all_trends
from app.ollama_client import ollama


def _template_review(
    emp_name: str,
    period: str,
    signals: list[dict],
    scores: list[dict],
    trends: dict,
) -> ReviewDraftResponse:
    """Template-based performance review."""
    highlights = []
    growth_areas = []
    risks = []
    suggested_goals = []

    if not signals:
        return ReviewDraftResponse(
            employee_name=emp_name,
            period=period,
            highlights=["Insufficient data for review."],
            growth_areas=[],
            risks=[],
            suggested_goals=[],
            summary="Not enough signal data to generate a review.",
            generated_by="template",
        )

    current = signals[0]
    score_map = {s["score_name"]: s for s in scores}

    # Highlights
    if current.get("tasks_completed", 0) >= 8:
        highlights.append(f"Completed {current['tasks_completed']} tasks this week, demonstrating strong execution.")
    if current.get("support_actions", 0) >= 4:
        highlights.append(f"Actively supported teammates with {current['support_actions']} collaborative actions.")
    if current.get("cross_team_ratio", 0) >= 0.35:
        highlights.append("Strong cross-team collaboration, contributing to organizational connectivity.")
    if current.get("learning_hours", 0) >= 3:
        highlights.append(f"Invested {current['learning_hours']}h in professional development.")
    if current.get("missed_deadlines", 0) == 0:
        highlights.append("Perfect on-time delivery record this period.")

    if not highlights:
        highlights.append("Maintained consistent contributions throughout the period.")

    # Growth areas
    task_trend = trends.get("tasks_completed", {}).get("direction", "stable")
    if task_trend == "increasing":
        growth_areas.append("Delivery velocity is increasing – potential for expanded scope.")
    if current.get("unique_collaborators", 0) < 5:
        growth_areas.append("Expand collaboration network to broaden impact and knowledge sharing.")
    if current.get("learning_hours", 0) < 1:
        growth_areas.append("Allocate time for skill development and continuous learning.")

    hp = score_map.get("high_potential", {})
    if hp.get("score", 0) >= 55:
        growth_areas.append("Shows high-potential signals – ready for stretch assignments.")

    # Risks
    br = score_map.get("burnout_risk", {})
    if br.get("score", 0) >= 50:
        risks.append(f"Burnout risk at {br['score']:.0f}/100. Monitor workload and well-being.")
    pd = score_map.get("performance_degradation", {})
    if pd.get("score", 0) >= 50:
        risks.append(f"Performance trend declining ({pd['score']:.0f}/100). Identify blockers.")
    if current.get("after_hours_events", 0) > 4:
        risks.append("Elevated after-hours activity suggests boundary issues.")

    # Goals
    suggested_goals.append("Maintain current delivery pace while protecting work-life balance.")
    if current.get("learning_hours", 0) < 2:
        suggested_goals.append("Complete at least one skill development activity per month.")
    if hp.get("score", 0) >= 55:
        suggested_goals.append("Take on a cross-functional initiative to expand leadership skills.")
    suggested_goals.append("Strengthen one cross-team relationship through a collaborative project.")

    summary = (
        f"{emp_name} has demonstrated {'strong' if len(highlights) >= 3 else 'steady'} performance "
        f"over the review period. "
        f"{'Key strengths include ' + highlights[0].lower() + '.' if highlights else ''} "
        f"{'Areas to watch: ' + risks[0].lower() if risks else 'No significant concerns identified.'}"
    )

    return ReviewDraftResponse(
        employee_name=emp_name,
        period=period,
        highlights=highlights,
        growth_areas=growth_areas,
        risks=risks,
        suggested_goals=suggested_goals,
        summary=summary.strip(),
        generated_by="template",
    )


async def _ollama_review(
    emp_name: str,
    period: str,
    signals: list[dict],
    scores: list[dict],
    trends: dict,
) -> ReviewDraftResponse | None:
    """Ollama-enhanced review generation."""
    system = (
        "You are a thoughtful management coach writing a performance review draft. "
        "Be specific, balanced, and constructive. Use data but maintain empathy. "
        "NEVER reference raw surveillance data. Only reference aggregated signals."
    )

    score_map = {s["score_name"]: s for s in scores}
    current = signals[0] if signals else {}

    prompt = f"""Write a performance review draft for {emp_name} for the period {period}.

Signal summary (4-week averages):
- Avg tasks completed/week: {sum(s.get('tasks_completed', 0) for s in signals[:4]) / max(len(signals[:4]), 1):.1f}
- Missed deadlines trend: {trends.get('missed_deadlines', {}).get('direction', 'N/A')}
- Meeting hours/week: {sum(s.get('meeting_hours', 0) for s in signals[:4]) / max(len(signals[:4]), 1):.1f}
- Focus blocks/week: {sum(s.get('focus_blocks', 0) for s in signals[:4]) / max(len(signals[:4]), 1):.1f}
- Cross-team collaboration: {current.get('cross_team_ratio', 0):.0%}
- Learning investment: {sum(s.get('learning_hours', 0) for s in signals[:4]) / max(len(signals[:4]), 1):.1f}h/week
- Support actions: {current.get('support_actions', 0)}/week

Computed assessments:
- Burnout risk: {score_map.get('burnout_risk', {}).get('score', 'N/A')}/100
- Growth potential: {score_map.get('high_potential', {}).get('score', 'N/A')}/100
- Performance trajectory: {score_map.get('performance_degradation', {}).get('score', 'N/A')}/100

Generate a structured review as JSON:
{{"highlights": ["..."], "growth_areas": ["..."], "risks": ["..."], "suggested_goals": ["..."], "summary": "2-3 sentence narrative"}}
"""

    result = await ollama.generate(prompt, system)
    if not result:
        return None

    try:
        start = result.find("{")
        end = result.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(result[start:end])
            return ReviewDraftResponse(
                employee_name=emp_name,
                period=period,
                highlights=data.get("highlights", []),
                growth_areas=data.get("growth_areas", []),
                risks=data.get("risks", []),
                suggested_goals=data.get("suggested_goals", []),
                summary=data.get("summary", ""),
                generated_by="ollama",
            )
    except (json.JSONDecodeError, KeyError):
        pass

    return None


async def generate_review(db: AsyncSession, employee_id: uuid.UUID) -> ReviewDraftResponse:
    """Generate a performance review draft for last 4 weeks."""
    emp = await db.get(Employee, employee_id)
    if not emp:
        raise ValueError(f"Employee {employee_id} not found")

    # Get last 8 weeks of signals
    result = await db.execute(
        select(WeeklySignal)
        .where(WeeklySignal.employee_id == employee_id)
        .order_by(WeeklySignal.week_start.desc())
        .limit(8)
    )
    signal_models = result.scalars().all()
    signals = [
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

    data_quality = signal_models[0].data_quality if signal_models else 1.0
    scores = compute_all_scores(signals, data_quality)
    trends = compute_all_trends(signals)

    today = date.today()
    period = f"{(today - timedelta(weeks=4)).isoformat()} to {today.isoformat()}"

    # Try Ollama, fall back to template
    ollama_result = await _ollama_review(emp.name, period, signals, scores, trends)
    if ollama_result:
        return ollama_result

    return _template_review(emp.name, period, signals, scores, trends)
