"""Synthetic demo data generator – realistic enterprise patterns.

Produces deterministic data when given a seed, so tests are repeatable.
Generates 8 weeks of weekly signals for each employee.
"""

from __future__ import annotations

import random
import uuid
from datetime import date, timedelta
from typing import NamedTuple

import numpy as np


class DemoEmployee(NamedTuple):
    name: str
    email: str
    role: str
    seniority: str
    tenure_months: int
    team: str
    department: str
    archetype: str  # healthy / overloaded / declining / rising_star / quiet_impact


# ── Archetypes define signal patterns ───────────────────────────────

ARCHETYPES = {
    "healthy": {
        "tasks_completed": (8, 2),
        "missed_deadlines": (0, 0.3),
        "workload_items": (10, 2),
        "cycle_time_days": (2.5, 0.5),
        "meeting_hours": (8, 2),
        "meeting_count": (10, 3),
        "fragmentation_score": (0.3, 0.1),
        "focus_blocks": (6, 1),
        "after_hours_events": (1, 1),
        "unique_collaborators": (8, 2),
        "cross_team_ratio": (0.3, 0.1),
        "support_actions": (3, 1),
        "learning_hours": (2, 1),
        "stretch_assignments": (0, 0.4),
        "skill_progress": (0.6, 0.1),
    },
    "overloaded": {
        "tasks_completed": (12, 2),
        "missed_deadlines": (2, 1),
        "workload_items": (18, 3),
        "cycle_time_days": (4.0, 1.0),
        "meeting_hours": (18, 3),
        "meeting_count": (22, 4),
        "fragmentation_score": (0.7, 0.1),
        "focus_blocks": (2, 1),
        "after_hours_events": (6, 2),
        "unique_collaborators": (5, 2),
        "cross_team_ratio": (0.15, 0.05),
        "support_actions": (1, 1),
        "learning_hours": (0, 0.5),
        "stretch_assignments": (0, 0.2),
        "skill_progress": (0.2, 0.1),
    },
    "declining": {
        "tasks_completed_trend": -0.5,  # per-week delta
        "tasks_completed": (7, 2),
        "missed_deadlines": (1, 0.5),
        "missed_deadlines_trend": 0.3,
        "workload_items": (12, 2),
        "cycle_time_days": (3.5, 0.8),
        "meeting_hours": (10, 2),
        "meeting_count": (12, 3),
        "fragmentation_score": (0.5, 0.1),
        "focus_blocks": (4, 1),
        "after_hours_events": (3, 1),
        "unique_collaborators": (6, 2),
        "cross_team_ratio": (0.2, 0.1),
        "support_actions": (2, 1),
        "learning_hours": (1, 0.5),
        "stretch_assignments": (0, 0.2),
        "skill_progress": (0.3, 0.1),
    },
    "rising_star": {
        "tasks_completed": (10, 2),
        "tasks_completed_trend": 0.3,
        "missed_deadlines": (0, 0.2),
        "workload_items": (11, 2),
        "cycle_time_days": (2.0, 0.3),
        "meeting_hours": (9, 2),
        "meeting_count": (11, 3),
        "fragmentation_score": (0.25, 0.08),
        "focus_blocks": (7, 1),
        "after_hours_events": (2, 1),
        "unique_collaborators": (10, 2),
        "cross_team_ratio": (0.4, 0.1),
        "support_actions": (4, 1),
        "learning_hours": (4, 1),
        "stretch_assignments": (1, 0.5),
        "skill_progress": (0.8, 0.1),
    },
    "quiet_impact": {
        "tasks_completed": (9, 1),
        "missed_deadlines": (0, 0.2),
        "workload_items": (10, 1),
        "cycle_time_days": (2.0, 0.3),
        "meeting_hours": (6, 1),
        "meeting_count": (7, 2),
        "fragmentation_score": (0.2, 0.05),
        "focus_blocks": (8, 1),
        "after_hours_events": (0, 0.5),
        "unique_collaborators": (12, 2),
        "cross_team_ratio": (0.5, 0.1),
        "support_actions": (6, 1),
        "learning_hours": (3, 1),
        "stretch_assignments": (1, 0.4),
        "skill_progress": (0.7, 0.1),
    },
}

# ── Demo employees ──────────────────────────────────────────────────

DEMO_EMPLOYEES: list[DemoEmployee] = [
    DemoEmployee("Alice Chen", "alice.chen@talentpulse.demo", "Senior Engineer", "Senior", 36, "Platform", "Engineering", "healthy"),
    DemoEmployee("Bob Martinez", "bob.martinez@talentpulse.demo", "Engineer", "Mid", 18, "Platform", "Engineering", "overloaded"),
    DemoEmployee("Carol Okafor", "carol.okafor@talentpulse.demo", "Tech Lead", "Lead", 48, "Platform", "Engineering", "declining"),
    DemoEmployee("David Kim", "david.kim@talentpulse.demo", "Junior Engineer", "Junior", 6, "Frontend", "Engineering", "rising_star"),
    DemoEmployee("Eva Novak", "eva.novak@talentpulse.demo", "Engineer", "Mid", 24, "Frontend", "Engineering", "quiet_impact"),
    DemoEmployee("Frank Torres", "frank.torres@talentpulse.demo", "Senior Engineer", "Senior", 30, "Backend", "Engineering", "healthy"),
    DemoEmployee("Grace Liu", "grace.liu@talentpulse.demo", "Product Manager", "Senior", 42, "Product", "Product", "overloaded"),
    DemoEmployee("Hassan Ali", "hassan.ali@talentpulse.demo", "Designer", "Mid", 15, "Design", "Design", "healthy"),
    DemoEmployee("Iris Patel", "iris.patel@talentpulse.demo", "Data Analyst", "Junior", 8, "Analytics", "Data", "rising_star"),
    DemoEmployee("James Wright", "james.wright@talentpulse.demo", "Senior Engineer", "Senior", 60, "Backend", "Engineering", "declining"),
    DemoEmployee("Keiko Tanaka", "keiko.tanaka@talentpulse.demo", "Engineer", "Mid", 20, "Backend", "Engineering", "quiet_impact"),
    DemoEmployee("Liam O'Brien", "liam.obrien@talentpulse.demo", "Junior Designer", "Junior", 4, "Design", "Design", "healthy"),
    DemoEmployee("Maria Santos", "maria.santos@talentpulse.demo", "Engineering Manager", "Lead", 54, "Platform", "Engineering", "overloaded"),
    DemoEmployee("Nina Petrov", "nina.petrov@talentpulse.demo", "QA Engineer", "Mid", 22, "QA", "Engineering", "healthy"),
    DemoEmployee("Omar Hassan", "omar.hassan@talentpulse.demo", "DevOps Engineer", "Senior", 33, "Infrastructure", "Engineering", "quiet_impact"),
]

# ── Skills catalog ──────────────────────────────────────────────────

SKILLS_BY_ROLE = {
    "Engineer": ["Python", "JavaScript", "SQL", "Docker", "Git", "REST APIs"],
    "Senior Engineer": ["Python", "System Design", "Mentoring", "SQL", "Cloud Architecture", "Performance Optimization"],
    "Junior Engineer": ["Python", "JavaScript", "Git", "HTML/CSS", "SQL", "Testing"],
    "Tech Lead": ["Architecture", "Code Review", "Mentoring", "Project Planning", "Python", "System Design"],
    "Product Manager": ["Roadmap Planning", "Stakeholder Mgmt", "Analytics", "User Research", "Agile", "Strategy"],
    "Designer": ["Figma", "UX Research", "Prototyping", "Design Systems", "User Testing"],
    "Junior Designer": ["Figma", "UI Design", "Wireframing", "Typography"],
    "Data Analyst": ["SQL", "Python", "Tableau", "Statistics", "Data Modeling"],
    "QA Engineer": ["Test Automation", "Selenium", "API Testing", "Performance Testing", "SQL"],
    "DevOps Engineer": ["Kubernetes", "Terraform", "CI/CD", "AWS", "Monitoring", "Linux"],
    "Engineering Manager": ["People Management", "Strategy", "Technical Vision", "Hiring", "Budget Planning"],
}


def generate_weekly_signals(
    archetype: str,
    num_weeks: int = 8,
    seed: int = 42,
) -> list[dict]:
    """Generate `num_weeks` of realistic weekly signals for an archetype.

    Returns list of dicts with signal keys + `week_offset` (0 = most recent).
    Deterministic when seed is fixed.
    """
    rng = np.random.default_rng(seed)
    params = ARCHETYPES[archetype]
    weeks = []

    for w in range(num_weeks):
        week_idx = num_weeks - 1 - w  # 0 = oldest, num_weeks-1 = newest
        row: dict = {}

        for key in [
            "tasks_completed", "missed_deadlines", "workload_items",
            "cycle_time_days", "meeting_hours", "meeting_count",
            "fragmentation_score", "focus_blocks", "after_hours_events",
            "unique_collaborators", "cross_team_ratio", "support_actions",
            "learning_hours", "stretch_assignments", "skill_progress",
        ]:
            mean, std = params.get(key, (0, 0))
            trend = params.get(f"{key}_trend", 0)
            val = rng.normal(mean + trend * week_idx, std)

            # Clamp per type
            if key in ("fragmentation_score", "cross_team_ratio", "skill_progress"):
                val = round(max(0.0, min(1.0, val)), 2)
            elif key in ("cycle_time_days", "meeting_hours", "learning_hours", "avg_meeting_length_min"):
                val = round(max(0.0, val), 1)
            else:
                val = max(0, int(round(val)))
            row[key] = val

        # Derived
        row["avg_meeting_length_min"] = round(
            (row["meeting_hours"] * 60 / max(row["meeting_count"], 1)), 1
        )
        row["response_time_bucket"] = rng.choice(
            ["fast", "normal", "slow"],
            p=[0.3, 0.5, 0.2] if archetype != "overloaded" else [0.15, 0.35, 0.5],
        )
        row["data_quality"] = round(rng.uniform(0.75, 1.0), 2)
        row["week_offset"] = w

        weeks.append(row)

    # Return with week 0 = most recent
    return list(reversed(weeks))


def generate_skills(role: str, seed: int = 42) -> list[dict]:
    """Generate skill set for a role."""
    rng = random.Random(seed)
    skills = SKILLS_BY_ROLE.get(role, ["General"])
    return [
        {
            "skill_name": s,
            "proficiency": rng.randint(1, 5),
            "is_growing": rng.random() > 0.5,
        }
        for s in skills
    ]


def get_demo_week_start(weeks_ago: int = 0) -> date:
    """Return the Monday of `weeks_ago` weeks before today."""
    today = date(2026, 2, 2)  # Fixed for deterministic demo
    monday = today - timedelta(days=today.weekday())
    return monday - timedelta(weeks=weeks_ago)
