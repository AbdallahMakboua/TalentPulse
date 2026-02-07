"""1:1 question generator – Ollama-enhanced with template fallback.

Manager Coaching Copilot: generates agenda, questions, listening cues, follow-ups.
"""

from __future__ import annotations

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Employee, WeeklySignal, EmployeeScore
from app.schemas import QuestionsResponse
from app.ollama_client import ollama


def _normalize_str_list(items: list) -> list[str]:
    """Ollama sometimes returns [{"key": "value"}, ...] instead of ["value", ...]. Flatten."""
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            for v in item.values():
                if isinstance(v, str):
                    result.append(v)
                    break
            else:
                result.append(str(item))
        else:
            result.append(str(item))
    return result


# ── Template fallback ───────────────────────────────────────────────

def _template_questions(emp_name: str, scores: dict, signals: dict) -> QuestionsResponse:
    """Rule-based 1:1 agenda generator – works without Ollama."""
    questions = []
    listening_cues = []
    follow_ups = []
    context_notes = []

    br = scores.get("burnout_risk", 0)
    pd = scores.get("performance_degradation", 0)
    hp = scores.get("high_potential", 0)
    pressure = scores.get("high_pressure", 0)

    # Always start warm
    questions.append(f"How are you feeling about your work this week, {emp_name}?")
    listening_cues.append("Listen for energy level, enthusiasm, and any hesitation.")

    # Burnout / pressure path
    if br >= 50 or pressure >= 55:
        questions.append("I've noticed your workload has been intense. What's been the most challenging part?")
        questions.append("Are there meetings or tasks we can deprioritize to give you more focus time?")
        listening_cues.append("Watch for signs of exhaustion, frustration, or disengagement.")
        follow_ups.append("Review and reduce meeting load by 20% next sprint.")
        follow_ups.append("Block protected focus time on calendar.")
        context_notes.append(f"Burnout risk score: {br:.0f}/100. After-hours activity: {signals.get('after_hours_events', 0)} events.")

    # Performance degradation path
    if pd >= 50:
        questions.append("Have you run into any blockers on your current projects?")
        questions.append("Is there support or context you need that you're not getting?")
        listening_cues.append("Avoid blame framing. Focus on systemic blockers, not individual shortcomings.")
        follow_ups.append("Identify and address top 2 blockers within this week.")
        context_notes.append(f"Performance trend declining. Missed deadlines: {signals.get('missed_deadlines', 0)}.")

    # High potential path
    if hp >= 55:
        questions.append("What skills are you most excited to develop right now?")
        questions.append("Would you be interested in a stretch assignment or mentorship opportunity?")
        follow_ups.append("Explore stretch project assignment for next quarter.")
        follow_ups.append("Connect with potential mentor in adjacent team.")
        context_notes.append(f"High potential score: {hp:.0f}/100. Growth trajectory strong.")

    # Collaboration
    if signals.get("unique_collaborators", 0) < 5:
        questions.append("How do you feel about your connections with other teams?")
        follow_ups.append("Introduce to cross-team stakeholders.")

    # Growth
    if signals.get("learning_hours", 0) >= 3:
        questions.append("I see you've been investing in learning. What are you working on?")
        context_notes.append(f"Learning hours: {signals.get('learning_hours', 0)}h this week.")

    # Ensure we always have meaningful depth (at least 3 questions before the close)
    if len(questions) < 3:
        questions.append("What's been the most rewarding part of your work recently?")
        listening_cues.append("Look for what energizes them — this reveals engagement drivers.")
    if len(questions) < 4:
        questions.append("Are there any process improvements you'd suggest for the team?")
        follow_ups.append("Document suggested improvements and review at next retrospective.")

    # General close
    questions.append("What's one thing I can do to better support you?")
    listening_cues.append("End with genuine curiosity. Take notes on commitments made.")
    follow_ups.append("Send summary of action items within 24 hours.")

    return QuestionsResponse(
        employee_name=emp_name,
        questions=questions,
        listening_cues=listening_cues,
        follow_up_actions=follow_ups,
        context_notes=context_notes,
        generated_by="template",
    )


# ── Ollama-enhanced generation ──────────────────────────────────────

async def _ollama_questions(emp_name: str, scores: dict, signals: dict) -> QuestionsResponse | None:
    """Use Ollama to generate rich 1:1 agenda."""
    system = (
        "You are an empathetic management coach. Generate a structured 1:1 meeting agenda. "
        "Be specific, action-oriented, and human-centered. Never blame the employee. "
        "Format: list questions, listening cues, follow-up actions, and context notes."
    )

    prompt = f"""Generate a 1:1 meeting agenda for {emp_name}.

Current signals (this week):
- Tasks completed: {signals.get('tasks_completed', 'N/A')}
- Missed deadlines: {signals.get('missed_deadlines', 'N/A')}
- Meeting hours: {signals.get('meeting_hours', 'N/A')}h
- Focus blocks (≥2h): {signals.get('focus_blocks', 'N/A')}
- After-hours events: {signals.get('after_hours_events', 'N/A')}
- Unique collaborators: {signals.get('unique_collaborators', 'N/A')}
- Learning hours: {signals.get('learning_hours', 'N/A')}h

Computed scores (0-100):
- Burnout risk: {scores.get('burnout_risk', 'N/A')}
- High pressure: {scores.get('high_pressure', 'N/A')}
- High potential: {scores.get('high_potential', 'N/A')}
- Performance degradation: {scores.get('performance_degradation', 'N/A')}

Generate exactly:
1. 5-7 open-ended questions (warm, specific, non-judgmental)
2. 3-4 listening cues for the manager
3. 3-5 concrete follow-up actions
4. 2-3 context notes about what data informed this

Respond in JSON format:
{{"questions": [...], "listening_cues": [...], "follow_up_actions": [...], "context_notes": [...]}}
"""

    result = await ollama.generate(prompt, system)
    if not result:
        return None

    # Parse the response (best-effort)
    import json
    try:
        # Try to extract JSON from response
        start = result.find("{")
        end = result.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(result[start:end])
            return QuestionsResponse(
                employee_name=emp_name,
                questions=_normalize_str_list(data.get("questions", [])),
                listening_cues=_normalize_str_list(data.get("listening_cues", [])),
                follow_up_actions=_normalize_str_list(data.get("follow_up_actions", [])),
                context_notes=_normalize_str_list(data.get("context_notes", [])),
                generated_by="ollama",
            )
    except (json.JSONDecodeError, KeyError, TypeError, Exception):
        pass

    return None


# ── Public API ──────────────────────────────────────────────────────

async def generate_questions(db: AsyncSession, employee_id: uuid.UUID) -> QuestionsResponse:
    """Generate 1:1 coaching agenda for an employee."""
    emp = await db.get(Employee, employee_id)
    if not emp:
        raise ValueError(f"Employee {employee_id} not found")

    # Get latest signals
    result = await db.execute(
        select(WeeklySignal)
        .where(WeeklySignal.employee_id == employee_id)
        .order_by(WeeklySignal.week_start.desc())
        .limit(1)
    )
    signal = result.scalar()
    signals = {
        "tasks_completed": signal.tasks_completed if signal else 0,
        "missed_deadlines": signal.missed_deadlines if signal else 0,
        "meeting_hours": signal.meeting_hours if signal else 0,
        "focus_blocks": signal.focus_blocks if signal else 0,
        "after_hours_events": signal.after_hours_events if signal else 0,
        "unique_collaborators": signal.unique_collaborators if signal else 0,
        "learning_hours": signal.learning_hours if signal else 0,
    }

    # Get latest scores
    score_result = await db.execute(
        select(EmployeeScore)
        .where(EmployeeScore.employee_id == employee_id)
        .order_by(EmployeeScore.week_start.desc())
        .limit(1)
    )
    score = score_result.scalar()
    scores = {
        "burnout_risk": score.burnout_risk if score else 0,
        "high_pressure": score.high_pressure if score else 0,
        "high_potential": score.high_potential if score else 0,
        "performance_degradation": score.performance_degradation if score else 0,
    }

    # Try Ollama first, fall back to template
    ollama_result = await _ollama_questions(emp.name, scores, signals)
    if ollama_result:
        return ollama_result

    return _template_questions(emp.name, scores, signals)
