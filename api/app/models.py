"""SQLAlchemy ORM models for TalentPulse."""

from __future__ import annotations

import uuid
from datetime import datetime, date

from sqlalchemy import (
    String, Integer, Float, Boolean, Date, DateTime, Text, JSON,
    ForeignKey, Index, UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


# ── Helpers ─────────────────────────────────────────────────────────

def _uuid():
    return uuid.uuid4()


def _now():
    return datetime.utcnow()


# ── Organization ────────────────────────────────────────────────────

class Team(Base):
    __tablename__ = "teams"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    department: Mapped[str] = mapped_column(String(200), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    employees: Mapped[list["Employee"]] = relationship(back_populates="team", lazy="selectin")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(300), nullable=False)
    email: Mapped[str] = mapped_column(String(300), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(200), default="Individual Contributor")
    seniority: Mapped[str] = mapped_column(String(100), default="Mid")  # Junior/Mid/Senior/Lead/Staff
    tenure_months: Mapped[int] = mapped_column(Integer, default=12)
    team_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    team: Mapped["Team"] = relationship(back_populates="employees", lazy="selectin")
    signals: Mapped[list["WeeklySignal"]] = relationship(back_populates="employee", lazy="selectin")
    scores: Mapped[list["EmployeeScore"]] = relationship(back_populates="employee", lazy="selectin")
    skills: Mapped[list["EmployeeSkill"]] = relationship(back_populates="employee", lazy="selectin")


# ── Signals ─────────────────────────────────────────────────────────

class WeeklySignal(Base):
    """Aggregated weekly signals per employee. One row per employee per week."""
    __tablename__ = "weekly_signals"
    __table_args__ = (
        UniqueConstraint("employee_id", "week_start", name="uq_signal_employee_week"),
        Index("ix_signal_week", "week_start"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)

    # Delivery
    tasks_completed: Mapped[int] = mapped_column(Integer, default=0)
    missed_deadlines: Mapped[int] = mapped_column(Integer, default=0)
    workload_items: Mapped[int] = mapped_column(Integer, default=0)
    cycle_time_days: Mapped[float] = mapped_column(Float, default=0.0)

    # Engagement
    meeting_hours: Mapped[float] = mapped_column(Float, default=0.0)
    meeting_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_meeting_length_min: Mapped[float] = mapped_column(Float, default=0.0)
    fragmentation_score: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1
    focus_blocks: Mapped[int] = mapped_column(Integer, default=0)  # >=2h uninterrupted

    # Responsiveness
    response_time_bucket: Mapped[str] = mapped_column(String(30), default="normal")  # fast/normal/slow
    after_hours_events: Mapped[int] = mapped_column(Integer, default=0)  # bucketed count

    # Collaboration
    unique_collaborators: Mapped[int] = mapped_column(Integer, default=0)
    cross_team_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    support_actions: Mapped[int] = mapped_column(Integer, default=0)  # code reviews, helps

    # Growth
    learning_hours: Mapped[float] = mapped_column(Float, default=0.0)
    stretch_assignments: Mapped[int] = mapped_column(Integer, default=0)
    skill_progress: Mapped[float] = mapped_column(Float, default=0.0)  # 0-1

    # Meta
    data_quality: Mapped[float] = mapped_column(Float, default=1.0)  # 0-1
    source: Mapped[str] = mapped_column(String(50), default="demo")  # demo / graph
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    employee: Mapped["Employee"] = relationship(back_populates="signals")


# ── Scores ──────────────────────────────────────────────────────────

class EmployeeScore(Base):
    """Computed scores per employee per week."""
    __tablename__ = "employee_scores"
    __table_args__ = (
        UniqueConstraint("employee_id", "week_start", name="uq_score_employee_week"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    week_start: Mapped[date] = mapped_column(Date, nullable=False)

    # Scores 0-100
    burnout_risk: Mapped[float] = mapped_column(Float, default=0.0)
    high_pressure: Mapped[float] = mapped_column(Float, default=0.0)
    high_potential: Mapped[float] = mapped_column(Float, default=0.0)
    performance_degradation: Mapped[float] = mapped_column(Float, default=0.0)

    # Labels
    burnout_label: Mapped[str] = mapped_column(String(20), default="Low")
    pressure_label: Mapped[str] = mapped_column(String(20), default="Low")
    potential_label: Mapped[str] = mapped_column(String(20), default="Low")
    degradation_label: Mapped[str] = mapped_column(String(20), default="Low")

    # Explainability (JSON)
    burnout_explanation: Mapped[dict] = mapped_column(JSON, default=dict)
    pressure_explanation: Mapped[dict] = mapped_column(JSON, default=dict)
    potential_explanation: Mapped[dict] = mapped_column(JSON, default=dict)
    degradation_explanation: Mapped[dict] = mapped_column(JSON, default=dict)

    # Confidence 0-1
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    limitations: Mapped[str] = mapped_column(Text, default="")

    # Bias info
    cohort_size: Mapped[int] = mapped_column(Integer, default=0)
    fairness_warning: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    employee: Mapped["Employee"] = relationship(back_populates="scores")


# ── Skills Matrix ───────────────────────────────────────────────────

class EmployeeSkill(Base):
    __tablename__ = "employee_skills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    employee_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(200), nullable=False)
    proficiency: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    is_growing: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    employee: Mapped["Employee"] = relationship(back_populates="skills")


# ── Settings ────────────────────────────────────────────────────────

class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    working_hours_start: Mapped[int] = mapped_column(Integer, default=9)
    working_hours_end: Mapped[int] = mapped_column(Integer, default=18)
    timezone: Mapped[str] = mapped_column(String(100), default="America/New_York")
    data_retention_days: Mapped[int] = mapped_column(Integer, default=90)
    demo_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_graph: Mapped[bool] = mapped_column(Boolean, default=False)
    scoring_weights: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
