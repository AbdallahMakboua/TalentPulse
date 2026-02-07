"""Pydantic schemas for API request / response."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Base ────────────────────────────────────────────────────────────

class TeamOut(BaseModel):
    id: uuid.UUID
    name: str
    department: str
    employee_count: int = 0

    model_config = {"from_attributes": True}


class EmployeeSummary(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: str
    seniority: str
    tenure_months: int
    team_name: str = ""
    team_id: uuid.UUID

    # Latest scores (optional – may not exist yet)
    burnout_risk: float = 0.0
    burnout_label: str = "N/A"
    high_potential: float = 0.0
    potential_label: str = "N/A"
    performance_degradation: float = 0.0
    degradation_label: str = "N/A"
    high_pressure: float = 0.0
    pressure_label: str = "N/A"

    model_config = {"from_attributes": True}


class SignalRow(BaseModel):
    week_start: date
    tasks_completed: int = 0
    missed_deadlines: int = 0
    workload_items: int = 0
    cycle_time_days: float = 0.0
    meeting_hours: float = 0.0
    meeting_count: int = 0
    avg_meeting_length_min: float = 0.0
    fragmentation_score: float = 0.0
    focus_blocks: int = 0
    response_time_bucket: str = "normal"
    after_hours_events: int = 0
    unique_collaborators: int = 0
    cross_team_ratio: float = 0.0
    support_actions: int = 0
    learning_hours: float = 0.0
    stretch_assignments: int = 0
    skill_progress: float = 0.0
    data_quality: float = 1.0

    model_config = {"from_attributes": True}


class ExplainabilityCard(BaseModel):
    score_name: str  # e.g. "burnout_risk"
    score: float
    label: str
    top_contributors: list[dict]  # [{signal, value, delta, direction}]
    trend_explanation: str
    confidence: float
    limitations: str
    fairness_warning: str = ""


class EmployeeInsights(BaseModel):
    employee: EmployeeSummary
    signals: list[SignalRow]
    scores: list[ExplainabilityCard]
    recommendations: list[str]
    hidden_talent: bool = False
    predictive_burnout: Optional[dict] = None
    skills: list[dict] = []

    model_config = {"from_attributes": True}


class QuestionsResponse(BaseModel):
    employee_name: str
    questions: list[str]
    listening_cues: list[str]
    follow_up_actions: list[str]
    context_notes: list[str]
    generated_by: str = "template"  # "template" | "ollama"


class ReviewDraftResponse(BaseModel):
    employee_name: str
    period: str
    highlights: list[str]
    growth_areas: list[str]
    risks: list[str]
    suggested_goals: list[str]
    summary: str
    generated_by: str = "template"


class OrgOverview(BaseModel):
    total_employees: int = 0
    total_teams: int = 0
    burnout_risk_distribution: dict = {}  # {Low: n, Med: n, High: n}
    pressure_distribution: dict = {}
    potential_distribution: dict = {}
    degradation_distribution: dict = {}
    trending_alerts: list[dict] = []
    overloaded_teams: list[dict] = []
    collaboration_bottlenecks: list[dict] = []


class TeamSummary(BaseModel):
    id: uuid.UUID
    name: str
    department: str
    employee_count: int = 0
    avg_burnout_risk: float = 0.0
    avg_high_potential: float = 0.0
    avg_performance_degradation: float = 0.0
    workload_imbalance: float = 0.0  # std dev of workload
    trend: str = "stable"  # improving / stable / declining


class SettingsIn(BaseModel):
    working_hours_start: Optional[int] = None
    working_hours_end: Optional[int] = None
    timezone: Optional[str] = None
    data_retention_days: Optional[int] = None
    demo_mode: Optional[bool] = None
    enable_graph: Optional[bool] = None
    scoring_weights: Optional[dict] = None


class SettingsOut(BaseModel):
    working_hours_start: int = 9
    working_hours_end: int = 18
    timezone: str = "America/New_York"
    data_retention_days: int = 90
    demo_mode: bool = True
    enable_graph: bool = False
    scoring_weights: dict = {}

    model_config = {"from_attributes": True}


class SyncResponse(BaseModel):
    status: str
    employees_processed: int = 0
    weeks_generated: int = 0
    scores_computed: int = 0
    message: str = ""
