"""Compute derived signals and aggregations from raw weekly signals."""

from __future__ import annotations

from datetime import date
from typing import Sequence

import numpy as np


def compute_trend(values: Sequence[float]) -> dict:
    """Compute linear trend over a time series.

    Returns dict with slope, direction, magnitude, and summary.
    """
    if len(values) < 2:
        return {"slope": 0.0, "direction": "stable", "magnitude": 0.0, "summary": "Insufficient data"}

    x = np.arange(len(values), dtype=float)
    y = np.array(values, dtype=float)

    # Simple linear regression
    slope = float(np.polyfit(x, y, 1)[0])
    magnitude = abs(slope)

    if magnitude < 0.1:
        direction = "stable"
    elif slope > 0:
        direction = "increasing"
    else:
        direction = "decreasing"

    return {
        "slope": round(slope, 3),
        "direction": direction,
        "magnitude": round(magnitude, 3),
        "summary": f"{'↗' if slope > 0.1 else '↘' if slope < -0.1 else '→'} {direction} (Δ{slope:+.2f}/week)",
    }


def compute_delta(current: float, previous: float) -> dict:
    """Compute absolute and percentage delta."""
    delta = current - previous
    pct = (delta / previous * 100) if previous != 0 else 0.0
    return {
        "delta": round(delta, 2),
        "pct_change": round(pct, 1),
        "direction": "up" if delta > 0 else "down" if delta < 0 else "flat",
    }


def compute_rolling_average(values: Sequence[float], window: int = 4) -> float:
    """4-week rolling average."""
    if not values:
        return 0.0
    recent = list(values)[-window:]
    return round(float(np.mean(recent)), 2)


def compute_workload_distribution(team_workloads: Sequence[float]) -> dict:
    """Analyse workload distribution across a team."""
    if len(team_workloads) < 2:
        return {"std_dev": 0, "imbalance": "N/A", "gini": 0}

    arr = np.array(team_workloads, dtype=float)
    std = float(np.std(arr))
    mean = float(np.mean(arr))

    # Simple Gini coefficient
    sorted_arr = np.sort(arr)
    n = len(sorted_arr)
    indices = np.arange(1, n + 1)
    gini = float((2 * np.sum(indices * sorted_arr) - (n + 1) * np.sum(sorted_arr)) / (n * np.sum(sorted_arr))) if np.sum(sorted_arr) > 0 else 0

    if std / max(mean, 1) > 0.5:
        imbalance = "High"
    elif std / max(mean, 1) > 0.25:
        imbalance = "Medium"
    else:
        imbalance = "Low"

    return {
        "std_dev": round(std, 2),
        "mean": round(mean, 2),
        "imbalance": imbalance,
        "gini": round(gini, 3),
    }


def compute_fragmentation(meeting_count: int, meeting_hours: float, focus_blocks: int) -> float:
    """Compute daily fragmentation score 0-1.

    High meeting count + low focus blocks = high fragmentation.
    """
    meetings_factor = min(meeting_count / 25, 1.0)  # 25+ meetings = max
    focus_factor = 1.0 - min(focus_blocks / 10, 1.0)  # 10+ blocks = min
    hours_factor = min(meeting_hours / 20, 1.0)  # 20+ hours = max

    score = 0.4 * meetings_factor + 0.3 * focus_factor + 0.3 * hours_factor
    return round(max(0.0, min(1.0, score)), 2)


def extract_signal_series(signals: list[dict], key: str) -> list[float]:
    """Extract a single signal across weeks, sorted oldest-first."""
    return [float(s.get(key, 0)) for s in signals]


def compute_all_trends(signals: list[dict]) -> dict[str, dict]:
    """Compute trends for all numeric signals."""
    if not signals:
        return {}

    trend_keys = [
        "tasks_completed", "missed_deadlines", "workload_items",
        "cycle_time_days", "meeting_hours", "meeting_count",
        "fragmentation_score", "focus_blocks", "after_hours_events",
        "unique_collaborators", "cross_team_ratio", "support_actions",
        "learning_hours", "stretch_assignments", "skill_progress",
    ]

    return {
        key: compute_trend(extract_signal_series(signals, key))
        for key in trend_keys
    }
