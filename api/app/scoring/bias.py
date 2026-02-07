"""Bias-aware normalization and fairness checks.

Compares employees against:
1. Their own historical baseline (primary)
2. Role/seniority cohort baseline (secondary)

Surfaces fairness warnings when cohort comparisons are unreliable.
"""

from __future__ import annotations

from typing import Sequence
import numpy as np


# ── Normalization ───────────────────────────────────────────────────

def compute_self_baseline(history: list[dict], key: str) -> dict:
    """Compute an employee's own historical baseline for a signal."""
    values = [float(h.get(key, 0)) for h in history if key in h]
    if len(values) < 2:
        return {"mean": 0, "std": 0, "n": len(values)}
    return {
        "mean": round(float(np.mean(values)), 2),
        "std": round(float(np.std(values)), 2),
        "n": len(values),
    }


def compute_cohort_baseline(cohort_values: Sequence[float]) -> dict:
    """Compute cohort baseline from peer values."""
    if len(cohort_values) < 2:
        return {"mean": 0, "std": 0, "n": len(cohort_values)}
    arr = np.array(cohort_values, dtype=float)
    return {
        "mean": round(float(np.mean(arr)), 2),
        "std": round(float(np.std(arr)), 2),
        "n": len(cohort_values),
    }


def z_score(value: float, baseline: dict) -> float:
    """How many standard deviations from baseline."""
    if baseline["std"] == 0 or baseline["n"] < 2:
        return 0.0
    return round((value - baseline["mean"]) / baseline["std"], 2)


def normalize_score_for_cohort(
    raw_score: float,
    self_baseline: dict,
    cohort_baseline: dict,
    self_weight: float = 0.7,
    cohort_weight: float = 0.3,
) -> dict:
    """Blend self-baseline and cohort-baseline normalization.

    Primary: compare vs own history (70%)
    Secondary: compare vs cohort (30%)
    """
    self_z = z_score(raw_score, self_baseline) if self_baseline["n"] >= 2 else 0
    cohort_z = z_score(raw_score, cohort_baseline) if cohort_baseline["n"] >= 3 else 0

    # Weighted blend
    if self_baseline["n"] >= 2 and cohort_baseline["n"] >= 3:
        blended = self_weight * self_z + cohort_weight * cohort_z
    elif self_baseline["n"] >= 2:
        blended = self_z
    elif cohort_baseline["n"] >= 3:
        blended = cohort_z
    else:
        blended = 0.0

    return {
        "self_z": self_z,
        "cohort_z": cohort_z,
        "blended_z": round(blended, 2),
        "self_baseline": self_baseline,
        "cohort_baseline": cohort_baseline,
    }


# ── Fairness warnings ──────────────────────────────────────────────

def check_fairness(
    employee_role: str,
    employee_seniority: str,
    cohort_size: int,
    comparison_roles: list[str] | None = None,
) -> dict:
    """Generate fairness warnings for bias-aware scoring.

    Returns warning dict with details.
    """
    warnings: list[str] = []
    severity = "none"

    # Small cohort warning
    if cohort_size < 5:
        warnings.append(
            f"Small cohort: only {cohort_size} peers in role/seniority group. "
            "Comparisons may be unreliable."
        )
        severity = "medium"

    if cohort_size < 3:
        warnings.append(
            "Cohort too small for meaningful comparison. "
            "Using self-baseline only."
        )
        severity = "high"

    # Role mismatch warning
    if comparison_roles:
        mismatched = [r for r in comparison_roles if r != employee_role]
        if len(mismatched) > len(comparison_roles) * 0.3:
            warnings.append(
                f"⚠ Fairness Note: Comparing across different roles ({employee_role} vs others). "
                "Baseline expectations may differ. Interpret with caution."
            )
            severity = "medium" if severity == "none" else severity

    # Seniority consideration
    junior_roles = {"Junior", "Intern", "Associate"}
    senior_roles = {"Senior", "Lead", "Staff", "Principal"}
    if employee_seniority in junior_roles:
        warnings.append(
            "Newer team member – give ramping time before drawing conclusions."
        )

    return {
        "warnings": warnings,
        "severity": severity,
        "cohort_size": cohort_size,
        "recommendation": (
            "Use self-baseline comparison primarily; treat cohort comparison as supplementary."
            if cohort_size < 5
            else "Both self and cohort baselines are reliable."
        ),
    }


def build_fairness_note(
    employee_role: str,
    employee_seniority: str,
    employee_tenure: int,
    cohort_size: int,
) -> str:
    """Build a human-readable fairness note for display."""
    parts = []

    if cohort_size < 5:
        parts.append(f"Small peer group ({cohort_size} in same role/level).")

    if employee_tenure < 6:
        parts.append("Newer team member — signals may reflect onboarding, not steady state.")

    if employee_seniority in ("Junior", "Intern"):
        parts.append("Junior level — different workload expectations apply.")

    if not parts:
        return ""

    return "⚠ Fairness Note: " + " ".join(parts)
