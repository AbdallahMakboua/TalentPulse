"""Tests for signal computation (trends, deltas, distributions)."""

import pytest
from app.signals.compute import (
    compute_trend,
    compute_delta,
    compute_rolling_average,
    compute_workload_distribution,
    compute_fragmentation,
    extract_signal_series,
    compute_all_trends,
)


class TestComputeTrend:
    def test_increasing_trend(self):
        values = [1, 2, 3, 4, 5]
        result = compute_trend(values)
        assert result["direction"] == "increasing"
        assert result["slope"] > 0

    def test_decreasing_trend(self):
        values = [5, 4, 3, 2, 1]
        result = compute_trend(values)
        assert result["direction"] == "decreasing"
        assert result["slope"] < 0

    def test_stable_trend(self):
        values = [5, 5, 5, 5, 5]
        result = compute_trend(values)
        assert result["direction"] == "stable"
        assert abs(result["slope"]) < 0.1

    def test_insufficient_data(self):
        result = compute_trend([5])
        assert result["direction"] == "stable"
        assert "Insufficient" in result["summary"]

    def test_empty_data(self):
        result = compute_trend([])
        assert result["direction"] == "stable"


class TestComputeDelta:
    def test_positive_delta(self):
        result = compute_delta(10, 5)
        assert result["delta"] == 5
        assert result["pct_change"] == 100.0
        assert result["direction"] == "up"

    def test_negative_delta(self):
        result = compute_delta(3, 5)
        assert result["delta"] == -2
        assert result["direction"] == "down"

    def test_zero_previous(self):
        result = compute_delta(5, 0)
        assert result["pct_change"] == 0.0

    def test_flat(self):
        result = compute_delta(5, 5)
        assert result["direction"] == "flat"


class TestRollingAverage:
    def test_basic_average(self):
        assert compute_rolling_average([1, 2, 3, 4]) == 2.5

    def test_window_limits(self):
        result = compute_rolling_average([1, 2, 3, 4, 5, 6, 7, 8], window=4)
        assert result == 6.5  # last 4: [5, 6, 7, 8]

    def test_empty(self):
        assert compute_rolling_average([]) == 0.0


class TestWorkloadDistribution:
    def test_balanced(self):
        result = compute_workload_distribution([10, 10, 10, 10])
        assert result["imbalance"] == "Low"

    def test_imbalanced(self):
        result = compute_workload_distribution([5, 5, 5, 25])
        assert result["imbalance"] in ("Medium", "High")

    def test_single_person(self):
        result = compute_workload_distribution([10])
        assert result["imbalance"] == "N/A"


class TestFragmentation:
    def test_high_fragmentation(self):
        score = compute_fragmentation(meeting_count=25, meeting_hours=20, focus_blocks=1)
        assert score >= 0.7

    def test_low_fragmentation(self):
        score = compute_fragmentation(meeting_count=5, meeting_hours=4, focus_blocks=8)
        assert score <= 0.3

    def test_bounds(self):
        score = compute_fragmentation(meeting_count=0, meeting_hours=0, focus_blocks=10)
        assert 0 <= score <= 1


class TestExtractSignalSeries:
    def test_extracts_values(self):
        signals = [{"tasks_completed": 5}, {"tasks_completed": 8}]
        result = extract_signal_series(signals, "tasks_completed")
        assert result == [5.0, 8.0]

    def test_missing_key_defaults_to_zero(self):
        signals = [{"other": 5}, {"other": 8}]
        result = extract_signal_series(signals, "tasks_completed")
        assert result == [0.0, 0.0]


class TestComputeAllTrends:
    def test_returns_trends_for_all_keys(self):
        signals = [
            {"tasks_completed": 5, "missed_deadlines": 0, "meeting_hours": 8},
            {"tasks_completed": 6, "missed_deadlines": 1, "meeting_hours": 9},
        ]
        trends = compute_all_trends(signals)
        assert "tasks_completed" in trends
        assert "missed_deadlines" in trends

    def test_empty_signals(self):
        assert compute_all_trends([]) == {}
