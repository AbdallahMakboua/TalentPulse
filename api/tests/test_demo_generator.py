"""Tests for demo data generator – must be deterministic."""

import pytest
from app.signals.generate_demo import (
    generate_weekly_signals, generate_skills, get_demo_week_start,
    DEMO_EMPLOYEES, ARCHETYPES,
)


class TestGenerateWeeklySignals:
    """Demo generator must produce deterministic, realistic data."""

    def test_generates_correct_number_of_weeks(self):
        signals = generate_weekly_signals("healthy", num_weeks=8, seed=42)
        assert len(signals) == 8

    def test_deterministic_with_same_seed(self):
        s1 = generate_weekly_signals("healthy", num_weeks=4, seed=42)
        s2 = generate_weekly_signals("healthy", num_weeks=4, seed=42)
        assert s1 == s2

    def test_different_seeds_produce_different_data(self):
        s1 = generate_weekly_signals("healthy", num_weeks=4, seed=42)
        s2 = generate_weekly_signals("healthy", num_weeks=4, seed=99)
        assert s1 != s2

    def test_all_archetypes_generate_valid_data(self):
        for archetype in ARCHETYPES:
            signals = generate_weekly_signals(archetype, num_weeks=4, seed=42)
            assert len(signals) == 4
            for s in signals:
                assert s["tasks_completed"] >= 0
                assert s["missed_deadlines"] >= 0
                assert 0 <= s["fragmentation_score"] <= 1
                assert 0 <= s["cross_team_ratio"] <= 1
                assert 0 <= s["skill_progress"] <= 1
                assert s["data_quality"] >= 0
                assert s["response_time_bucket"] in ("fast", "normal", "slow")

    def test_overloaded_archetype_has_higher_meeting_hours(self):
        healthy = generate_weekly_signals("healthy", num_weeks=8, seed=42)
        overloaded = generate_weekly_signals("overloaded", num_weeks=8, seed=42)
        avg_healthy = sum(s["meeting_hours"] for s in healthy) / len(healthy)
        avg_overloaded = sum(s["meeting_hours"] for s in overloaded) / len(overloaded)
        assert avg_overloaded > avg_healthy

    def test_rising_star_has_more_learning_hours(self):
        healthy = generate_weekly_signals("healthy", num_weeks=8, seed=42)
        rising = generate_weekly_signals("rising_star", num_weeks=8, seed=42)
        avg_healthy = sum(s["learning_hours"] for s in healthy) / len(healthy)
        avg_rising = sum(s["learning_hours"] for s in rising) / len(rising)
        assert avg_rising > avg_healthy

    def test_quiet_impact_has_high_support_actions(self):
        signals = generate_weekly_signals("quiet_impact", num_weeks=8, seed=42)
        avg_support = sum(s["support_actions"] for s in signals) / len(signals)
        assert avg_support >= 3  # quiet impact archetype has high support


class TestGenerateSkills:
    def test_generates_skills_for_role(self):
        skills = generate_skills("Senior Engineer", seed=42)
        assert len(skills) > 0
        assert all("skill_name" in s for s in skills)
        assert all(1 <= s["proficiency"] <= 5 for s in skills)

    def test_deterministic(self):
        s1 = generate_skills("Engineer", seed=42)
        s2 = generate_skills("Engineer", seed=42)
        assert s1 == s2


class TestDemoEmployees:
    def test_has_enough_employees(self):
        assert len(DEMO_EMPLOYEES) >= 10

    def test_all_archetypes_represented(self):
        archetypes = {e.archetype for e in DEMO_EMPLOYEES}
        assert "healthy" in archetypes
        assert "overloaded" in archetypes
        assert "declining" in archetypes
        assert "rising_star" in archetypes
        assert "quiet_impact" in archetypes

    def test_multiple_teams(self):
        teams = {e.team for e in DEMO_EMPLOYEES}
        assert len(teams) >= 4


class TestGetDemoWeekStart:
    def test_returns_monday(self):
        ws = get_demo_week_start(0)
        assert ws.weekday() == 0  # Monday

    def test_weeks_ago_decreases_date(self):
        w0 = get_demo_week_start(0)
        w1 = get_demo_week_start(1)
        assert w1 < w0
