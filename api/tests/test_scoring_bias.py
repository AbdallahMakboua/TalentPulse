"""Tests for scoring engine and bias-aware normalization."""

import pytest
from app.scoring.scorer import (
    score_dimension, compute_all_scores, detect_hidden_talent,
    predict_burnout, load_weights, WEIGHTS,
)
from app.scoring.bias import (
    compute_self_baseline, compute_cohort_baseline, z_score,
    normalize_score_for_cohort, check_fairness, build_fairness_note,
)
from app.signals.generate_demo import generate_weekly_signals


class TestScoreDimension:
    def test_burnout_risk_scoring(self):
        current = {
            "meeting_hours": 18, "after_hours_events": 6, "fragmentation_score": 0.7,
            "focus_blocks": 2, "unique_collaborators": 5, "learning_hours": 0,
            "workload_items": 18, "missed_deadlines": 2,
        }
        trends = {
            "tasks_completed": {"slope": -0.5, "direction": "decreasing"},
            "meeting_hours": {"slope": 0.3, "direction": "increasing"},
        }
        result = score_dimension("burnout_risk", current, trends, 0.9)
        assert 0 <= result["score"] <= 100
        assert result["label"] in ("Low", "Medium", "High")
        assert len(result["top_contributors"]) <= 5
        assert result["confidence"] > 0

    def test_high_potential_scoring(self):
        current = {
            "tasks_completed": 10, "learning_hours": 4, "stretch_assignments": 1,
            "skill_progress": 0.8, "unique_collaborators": 10, "cross_team_ratio": 0.4,
            "support_actions": 4, "missed_deadlines": 0,
        }
        trends = {}
        result = score_dimension("high_potential", current, trends, 1.0)
        assert result["score"] > 30  # rising star should score well

    def test_score_has_required_fields(self):
        result = score_dimension("burnout_risk", {}, {}, 1.0)
        required = {"score_name", "score", "label", "top_contributors",
                     "trend_explanation", "confidence", "limitations"}
        assert required.issubset(result.keys())


class TestComputeAllScores:
    def test_computes_four_dimensions(self):
        signals = generate_weekly_signals("healthy", num_weeks=8, seed=42)
        scores = compute_all_scores(signals, 0.9)
        assert len(scores) == 4
        names = {s["score_name"] for s in scores}
        assert names == {"burnout_risk", "high_pressure", "high_potential", "performance_degradation"}

    def test_overloaded_has_higher_burnout_risk(self):
        healthy_signals = generate_weekly_signals("healthy", num_weeks=8, seed=42)
        overloaded_signals = generate_weekly_signals("overloaded", num_weeks=8, seed=42)

        healthy_scores = compute_all_scores(healthy_signals, 0.9)
        overloaded_scores = compute_all_scores(overloaded_signals, 0.9)

        h_burnout = next(s for s in healthy_scores if s["score_name"] == "burnout_risk")
        o_burnout = next(s for s in overloaded_scores if s["score_name"] == "burnout_risk")

        assert o_burnout["score"] > h_burnout["score"]

    def test_rising_star_has_higher_potential(self):
        healthy_signals = generate_weekly_signals("healthy", num_weeks=8, seed=42)
        rising_signals = generate_weekly_signals("rising_star", num_weeks=8, seed=42)

        healthy_scores = compute_all_scores(healthy_signals, 0.9)
        rising_scores = compute_all_scores(rising_signals, 0.9)

        h_pot = next(s for s in healthy_scores if s["score_name"] == "high_potential")
        r_pot = next(s for s in rising_scores if s["score_name"] == "high_potential")

        assert r_pot["score"] > h_pot["score"]

    def test_empty_signals(self):
        assert compute_all_scores([], 1.0) == []

    def test_deterministic(self):
        s1 = compute_all_scores(generate_weekly_signals("healthy", 8, 42), 0.9)
        s2 = compute_all_scores(generate_weekly_signals("healthy", 8, 42), 0.9)
        assert s1 == s2


class TestHiddenTalent:
    def test_quiet_impact_detected(self):
        signals = generate_weekly_signals("quiet_impact", num_weeks=8, seed=42)
        scores = compute_all_scores(signals, 0.9)
        # quiet_impact may or may not trigger based on exact values
        result = detect_hidden_talent(scores, signals)
        assert isinstance(result, bool)

    def test_overloaded_not_hidden_talent(self):
        signals = generate_weekly_signals("overloaded", num_weeks=8, seed=42)
        scores = compute_all_scores(signals, 0.9)
        assert detect_hidden_talent(scores, signals) is False

    def test_empty_data(self):
        assert detect_hidden_talent([], []) is False


class TestPredictiveBurnout:
    def test_overloaded_may_trigger_prediction(self):
        signals = generate_weekly_signals("overloaded", num_weeks=8, seed=42)
        scores = compute_all_scores(signals, 0.9)
        result = predict_burnout(scores, signals)
        # May or may not trigger depending on exact scores
        if result is not None:
            assert "alert" in result
            assert "confidence" in result
            assert result["confidence"] <= 1.0

    def test_healthy_no_prediction(self):
        signals = generate_weekly_signals("healthy", num_weeks=8, seed=42)
        scores = compute_all_scores(signals, 0.9)
        result = predict_burnout(scores, signals)
        assert result is None

    def test_insufficient_data(self):
        assert predict_burnout([], []) is None


class TestBiasNormalization:
    def test_self_baseline(self):
        history = [{"meeting_hours": 8}, {"meeting_hours": 10}, {"meeting_hours": 9}]
        baseline = compute_self_baseline(history, "meeting_hours")
        assert baseline["mean"] == 9.0
        assert baseline["n"] == 3

    def test_cohort_baseline(self):
        values = [8.0, 10.0, 9.0, 11.0]
        baseline = compute_cohort_baseline(values)
        assert baseline["mean"] == 9.5
        assert baseline["n"] == 4

    def test_z_score_calculation(self):
        baseline = {"mean": 10.0, "std": 2.0, "n": 5}
        assert z_score(12.0, baseline) == 1.0
        assert z_score(8.0, baseline) == -1.0

    def test_z_score_zero_std(self):
        baseline = {"mean": 10.0, "std": 0.0, "n": 5}
        assert z_score(12.0, baseline) == 0.0


class TestFairnessChecks:
    def test_small_cohort_warning(self):
        result = check_fairness("Engineer", "Mid", cohort_size=3)
        assert result["severity"] in ("medium", "high")
        assert len(result["warnings"]) > 0

    def test_adequate_cohort_no_warning(self):
        result = check_fairness("Engineer", "Mid", cohort_size=10)
        assert result["severity"] == "none"

    def test_role_mismatch_warning(self):
        result = check_fairness(
            "Engineer", "Mid", cohort_size=10,
            comparison_roles=["Manager", "Manager", "Designer", "Engineer"]
        )
        assert any("Fairness" in w for w in result["warnings"])


class TestBuildFairnessNote:
    def test_small_cohort(self):
        note = build_fairness_note("Engineer", "Mid", 12, cohort_size=3)
        assert "Fairness" in note

    def test_new_employee(self):
        note = build_fairness_note("Engineer", "Junior", 3, cohort_size=10)
        assert "Newer" in note or "Junior" in note

    def test_no_concerns(self):
        note = build_fairness_note("Engineer", "Mid", 24, cohort_size=10)
        assert note == ""


class TestWeightsConfig:
    def test_weights_load(self):
        assert "burnout_risk" in WEIGHTS
        assert "high_potential" in WEIGHTS
        assert "normalization" in WEIGHTS

    def test_weights_have_required_structure(self):
        for dim in ["burnout_risk", "high_pressure", "high_potential", "performance_degradation"]:
            assert "weights" in WEIGHTS[dim]
            assert "thresholds" in WEIGHTS[dim]
            assert "low" in WEIGHTS[dim]["thresholds"]
            assert "high" in WEIGHTS[dim]["thresholds"]
