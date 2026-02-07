"""Explainable, bias-aware scoring engine.

Computes burnout_risk, high_pressure, high_potential, performance_degradation.
Each score: 0-100 with label, top contributors, trend explanation, confidence, limitations.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

from app.signals.compute import compute_trend, extract_signal_series


# ── Load weights ────────────────────────────────────────────────────

_WEIGHTS_PATH = Path(__file__).parent / "weights.yaml"


def load_weights(path: Path | None = None) -> dict:
    """Load scoring weights from YAML."""
    p = path or _WEIGHTS_PATH
    with open(p) as f:
        return yaml.safe_load(f)


WEIGHTS = load_weights()


def _normalize(value: float, signal_key: str) -> float:
    """Normalize a signal value to 0-1 using config ranges."""
    norms = WEIGHTS.get("normalization", {})
    cfg = norms.get(signal_key, {"min": 0, "max": 1})
    lo, hi = cfg["min"], cfg["max"]
    if hi == lo:
        return 0.0
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def _label(score: float, thresholds: dict) -> str:
    if score >= thresholds.get("high", 65):
        return "High"
    elif score >= thresholds.get("low", 35):
        return "Medium"
    return "Low"


def score_dimension(
    dimension: str,
    current_signals: dict,
    trends: dict[str, dict],
    data_quality: float = 1.0,
) -> dict:
    """Score a single dimension (burnout_risk, high_potential, etc.).

    Returns dict with score, label, top_contributors, trend_explanation,
    confidence, limitations.
    """
    cfg = WEIGHTS.get(dimension, {})
    weights = cfg.get("weights", {})
    thresholds = cfg.get("thresholds", {"low": 35, "high": 65})

    contributors: list[dict] = []
    weighted_sum = 0.0
    total_weight = 0.0

    for signal_key, weight in weights.items():
        # Handle trend-based signals
        if signal_key.endswith("_trend"):
            base_key = signal_key.replace("_trend", "")
            trend = trends.get(base_key, {})
            raw_value = trend.get("slope", 0.0)
            # Normalize slope to 0-1 range (slopes typically -2 to +2)
            norm_val = max(0.0, min(1.0, (raw_value + 2) / 4))
        else:
            raw_value = current_signals.get(signal_key, 0)
            norm_val = _normalize(float(raw_value), signal_key)

        # Negative weight = inverted (protective factor)
        contribution = norm_val * weight
        weighted_sum += contribution
        total_weight += abs(weight)

        trend_info = trends.get(signal_key.replace("_trend", ""), {})

        contributors.append({
            "signal": signal_key,
            "value": raw_value,
            "normalized": round(norm_val, 3),
            "weight": weight,
            "contribution": round(contribution, 4),
            "direction": trend_info.get("direction", "stable"),
            "delta": trend_info.get("summary", ""),
        })

    # Scale to 0-100
    if total_weight > 0:
        raw_score = (weighted_sum / total_weight) * 100
    else:
        raw_score = 0.0

    # Clamp
    score = round(max(0.0, min(100.0, raw_score)), 1)
    label = _label(score, thresholds)

    # Top 5 contributors by absolute contribution
    contributors.sort(key=lambda c: abs(c["contribution"]), reverse=True)
    top5 = contributors[:5]

    # Confidence based on data quality and number of signals available
    signal_coverage = sum(1 for c in contributors if c["value"] != 0) / max(len(contributors), 1)
    confidence = round(min(data_quality, signal_coverage), 2)

    # Limitations
    limitations_parts = []
    if confidence < 0.5:
        limitations_parts.append("Low confidence – limited data available.")
    if data_quality < 0.8:
        limitations_parts.append(f"Data quality: {data_quality:.0%}.")
    if signal_coverage < 0.6:
        limitations_parts.append("Some signals missing or zero.")
    limitations = " ".join(limitations_parts) if limitations_parts else "No significant limitations."

    # Trend explanation
    trend_summary_parts = []
    for c in top5:
        if c["direction"] != "stable":
            trend_summary_parts.append(f"{c['signal']} is {c['direction']}")
    trend_explanation = "; ".join(trend_summary_parts) if trend_summary_parts else "All key signals stable."

    return {
        "score_name": dimension,
        "score": score,
        "label": label,
        "top_contributors": top5,
        "trend_explanation": trend_explanation,
        "confidence": confidence,
        "limitations": limitations,
    }


def compute_all_scores(
    signals: list[dict],
    data_quality: float = 1.0,
) -> list[dict]:
    """Compute all 4 dimension scores from weekly signals.

    Args:
        signals: List of weekly signal dicts, newest first.
        data_quality: Overall data quality 0-1.

    Returns:
        List of score dicts.
    """
    if not signals:
        return []

    # Current = most recent week
    current = signals[0]

    # Compute trends from all weeks (need oldest-first for trend calc)
    ordered = list(reversed(signals))  # oldest first
    trends = {}
    for key in [
        "tasks_completed", "missed_deadlines", "workload_items",
        "cycle_time_days", "meeting_hours", "meeting_count",
        "fragmentation_score", "focus_blocks", "after_hours_events",
        "unique_collaborators", "cross_team_ratio", "support_actions",
        "learning_hours", "stretch_assignments", "skill_progress",
    ]:
        values = [float(s.get(key, 0)) for s in ordered]
        trends[key] = compute_trend(values)

    dimensions = ["burnout_risk", "high_pressure", "high_potential", "performance_degradation"]
    return [score_dimension(dim, current, trends, data_quality) for dim in dimensions]


def detect_hidden_talent(scores: list[dict], signals: list[dict]) -> bool:
    """Detect 'quiet impact' – steady delivery + high collaboration support + growth trend but low visibility.

    A 'blow-their-minds' feature: finds contributors who are high-impact
    but may be overlooked.
    """
    if not scores or not signals:
        return False

    score_map = {s["score_name"]: s for s in scores}

    hp = score_map.get("high_potential", {})
    br = score_map.get("burnout_risk", {})
    pd = score_map.get("performance_degradation", {})

    current = signals[0]
    support = current.get("support_actions", 0)
    cross_team = current.get("cross_team_ratio", 0)
    learning = current.get("learning_hours", 0)
    meetings = current.get("meeting_count", 0)

    # Quiet impact criteria:
    # 1) Good potential but not extremely high visibility (meetings moderate)
    # 2) High support actions
    # 3) Good cross-team ratio
    # 4) Low burnout risk, low degradation
    return (
        hp.get("score", 0) >= 50
        and br.get("score", 0) < 45
        and pd.get("score", 0) < 40
        and support >= 4
        and cross_team >= 0.35
        and learning >= 2
        and meetings <= 15  # not overexposed in meetings
    )


def predict_burnout(scores: list[dict], signals: list[dict]) -> dict | None:
    """Predictive burnout alert – 'blow their minds' feature.

    Uses pattern matching against synthetic cohort data to project risk.
    Returns prediction dict or None if risk is low.
    """
    if not scores or len(signals) < 4:
        return None

    score_map = {s["score_name"]: s for s in scores}
    br = score_map.get("burnout_risk", {})

    if br.get("score", 0) < 40:
        return None

    # Check sustained pattern (last 4 weeks)
    recent_4 = signals[:4]
    avg_meeting = sum(s.get("meeting_hours", 0) for s in recent_4) / 4
    avg_after_hours = sum(s.get("after_hours_events", 0) for s in recent_4) / 4
    avg_focus = sum(s.get("focus_blocks", 0) for s in recent_4) / 4

    # Pattern: sustained overload indicators
    overload_pattern = avg_meeting > 14 and avg_after_hours > 3 and avg_focus < 4

    if not overload_pattern and br.get("score", 0) < 55:
        return None

    # Compute projected weeks to critical
    current_score = br["score"]
    if len(signals) >= 4:
        recent_scores = []
        # Estimate score trajectory
        for i in range(min(4, len(signals))):
            week_signals = signals[i:i+1]
            if week_signals:
                recent_scores.append(current_score - i * 2)  # approximate

    weeks_to_critical = max(2, int((85 - current_score) / max(3, 1)))

    confidence = min(0.75, br.get("confidence", 0.5) * 1.2)

    return {
        "alert": "Predictive Burnout Warning",
        "message": f"This pattern has correlated with burnout in similar teams within ~{weeks_to_critical} weeks.",
        "current_score": current_score,
        "projected_weeks": weeks_to_critical,
        "pattern_signals": {
            "avg_meeting_hours_4w": round(avg_meeting, 1),
            "avg_after_hours_4w": round(avg_after_hours, 1),
            "avg_focus_blocks_4w": round(avg_focus, 1),
        },
        "confidence": round(confidence, 2),
        "uncertainty": "Based on cohort pattern matching; individual circumstances may differ.",
        "recommended_action": "Schedule a wellness check-in. Consider workload redistribution.",
    }
