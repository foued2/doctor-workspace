"""
S-Efficiency Layer — Binary regime classifier (disjoint branches)
==================================================================
S measures EXECUTION EFFICIENCY, not correctness or completeness.

S answers: "Is this solution computationally sane or wasteful?"

S_final = S_observed / S_ref
  - S_observed = total execution time (ms) across all test cases
  - S_ref = baseline execution time for canonical solution on same tests

*** PHASE 0 FREEZE ***
S_final, slope_ratio, and efficiency labels are DISABLED for decision-making.
S is READ-ONLY research output only. It is NEVER used to influence verdict
or confidence in the production flow.

INVARIANT: s_kind defines whether efficiency classification exists.
The output space is determined DISJOINTLY by s_kind:

  s_kind in {linear}:
    → output space = {not_applicable} ONLY
    → S_final value is recorded but NEVER used for classification
    → No threshold applies

  s_kind in {search, graph, dp, quadratic, log_linear}:
    → output space = {efficient, inefficient}
    → S_final < S_THRESHOLD → efficient
    → S_final >= S_THRESHOLD → inefficient

  s_kind = unknown (no registry entry):
    → output space = {not_applicable}

This is NOT a cascade. The branch is determined by s_kind alone,
and the output space is fixed within each branch.

Phase 1 findings:
  - Strong signal: brute vs (correct + partial) — orders of magnitude gap
  - Weak signal: correct vs partial — inconsistent, sometimes inverted
  - S is a binary discriminator of efficiency regimes, not tri-class separator
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════
# S_ref REGISTRY — canonical execution times per problem
# ═══════════════════════════════════════════════════════════
# Format: {problem_key: {"s_ref_ms": float, "s_kind": str}}
#
# s_kind determines the output space for efficiency:
#   "linear"      → not_applicable (S is meaningless for O(n))
#   "log_linear"  → efficient / inefficient
#   "quadratic"   → efficient / inefficient
#   "search"      → efficient / inefficient
#   "graph"       → efficient / inefficient
#   "dp"          → efficient / inefficient

S_KIND_NO_EFFICIENCY = {"linear"}  # s_kinds where S is never classified
S_KIND_HAS_EFFICIENCY = {"search", "graph", "dp", "quadratic", "log_linear"}

S_REF_REGISTRY: Dict[str, dict] = {
    "Two Sum":                {"s_ref_ms": 0.021, "s_kind": "linear"},
    "Palindrome Number":      {"s_ref_ms": 0.015, "s_kind": "linear"},
    "Roman to Integer":       {"s_ref_ms": 0.020, "s_kind": "linear"},
    "Valid Parentheses":      {"s_ref_ms": 0.015, "s_kind": "linear"},
    "Merge Two Sorted Lists": {"s_ref_ms": 0.025, "s_kind": "linear"},
    "Longest Palindromic Substring": {"s_ref_ms": 0.030, "s_kind": "quadratic"},
    "Container With Most Water": {"s_ref_ms": 0.013, "s_kind": "linear"},
    "Trapping Rain Water":   {"s_ref_ms": 0.023, "s_kind": "linear"},
    "N-Queens":              {"s_ref_ms": 0.053, "s_kind": "search"},
    "Median of Two Sorted Arrays": {"s_ref_ms": 0.015, "s_kind": "log_linear"},
}

# Threshold: S_final >= this → "inefficient" (only for s_kind in S_KIND_HAS_EFFICIENCY)
S_THRESHOLD = 10.0


@dataclass
class EfficiencyResult:
    s_observed_ms: float       # total execution time in ms
    s_ref_ms: float            # reference execution time in ms
    s_final: float             # normalized: s_observed / s_ref
    efficiency: str            # "efficient" | "inefficient" | "not_applicable"
    s_kind: str                # problem complexity kind
    efficiency_applicable: bool  # True if s_kind supports efficiency classification
    research_only: bool = True   # PHASE 0: ALWAYS True — S is not used for decisions


def compute_efficiency(
    traces: List[dict],
    problem_key: str,
    s_ref_override: Optional[float] = None,
    s_kind_override: Optional[str] = None,
) -> EfficiencyResult:
    """Compute S_final efficiency from execution traces.

    Classification follows disjoint branches determined by s_kind:
      - linear → always not_applicable
      - search/graph/dp/quadratic/log_linear → efficient or inefficient
      - unknown → not_applicable
    """
    # Sum total execution time across all test cases (convert to ms)
    total_ms = sum(t.get("execution_time", 0.0) * 1000.0 for t in traces) if traces else 0.0

    # Look up S_ref
    registry_entry = S_REF_REGISTRY.get(problem_key, {})
    s_ref = s_ref_override or registry_entry.get("s_ref_ms", None)
    s_kind = s_kind_override or registry_entry.get("s_kind", None)

    # ── BRANCH 1: No registry entry → not_applicable ──
    if s_ref is None or s_ref <= 0 or s_kind is None:
        return EfficiencyResult(
            s_observed_ms=round(total_ms, 4),
            s_ref_ms=0.0,
            s_final=0.0,
            efficiency="not_applicable",
            s_kind=s_kind or "unknown",
            efficiency_applicable=False,
            research_only=True,
        )

    s_final = total_ms / s_ref

    # ── BRANCH 2: Linear problem → always not_applicable ──
    # S_final is recorded but NEVER used for classification.
    # Even if S_final is 1000x, a linear problem stays not_applicable.
    if s_kind in S_KIND_NO_EFFICIENCY:
        return EfficiencyResult(
            s_observed_ms=round(total_ms, 4),
            s_ref_ms=s_ref,
            s_final=round(s_final, 2),
            efficiency="not_applicable",
            s_kind=s_kind,
            efficiency_applicable=False,
            research_only=True,
        )

    # ── BRANCH 3: Non-linear → binary classification ──
    if s_kind in S_KIND_HAS_EFFICIENCY:
        if s_final >= S_THRESHOLD:
            efficiency = "inefficient"
        else:
            efficiency = "efficient"
        return EfficiencyResult(
            s_observed_ms=round(total_ms, 4),
            s_ref_ms=s_ref,
            s_final=round(s_final, 2),
            efficiency=efficiency,
            s_kind=s_kind,
            efficiency_applicable=True,
            research_only=True,
        )

    # ── BRANCH 4: Unknown s_kind → not_applicable ──
    return EfficiencyResult(
        s_observed_ms=round(total_ms, 4),
        s_ref_ms=s_ref,
        s_final=round(s_final, 2),
        efficiency="not_applicable",
        s_kind=s_kind,
        efficiency_applicable=False,
        research_only=True,
    )


def efficiency_to_dict(result: EfficiencyResult) -> dict:
    """Convert EfficiencyResult to a JSON-serializable dict."""
    return {
        "s_observed_ms": result.s_observed_ms,
        "s_ref_ms": result.s_ref_ms,
        "s_final": result.s_final,
        "efficiency": result.efficiency,
        "s_kind": result.s_kind,
        "efficiency_applicable": result.efficiency_applicable,
        "research_only": result.research_only,
    }


# ═══════════════════════════════════════════════════════════
# SELF-TEST (includes the invariant test)
# ═══════════════════════════════════════════════════════════

def _self_test():
    """Verify S_efficiency logic on known cases, including the disjoint invariant."""
    # Case 1: N-Queens correct (search → efficient, S_final < 10)
    r = compute_efficiency(
        traces=[{"execution_time": 0.00005}],  # 0.05ms
        problem_key="N-Queens",
    )
    assert r.s_ref_ms == 0.053
    assert r.s_final == round(0.05 / 0.053, 2)
    assert r.efficiency == "efficient"
    assert r.efficiency_applicable is True
    print(f"  N-Queens correct: S_final={r.s_final} → {r.efficiency} ✓")

    # Case 2: N-Queens brute (search → inefficient, S_final >= 10)
    r = compute_efficiency(
        traces=[{"execution_time": 0.001}],  # 1ms = ~19x ref
        problem_key="N-Queens",
    )
    assert r.s_final == round(1.0 / 0.053, 2)
    assert r.efficiency == "inefficient"
    assert r.efficiency_applicable is True
    print(f"  N-Queens brute: S_final={r.s_final} → {r.efficiency} ✓")

    # Case 3: Two Sum (linear → always not_applicable, low S_final)
    r = compute_efficiency(
        traces=[{"execution_time": 0.00002}],  # 0.02ms, S_final=0.95
        problem_key="Two Sum",
    )
    assert r.efficiency == "not_applicable"
    assert r.efficiency_applicable is False
    print(f"  Two Sum (low S): S_final={r.s_final} → {r.efficiency} (linear) ✓")

    # Case 4: INVARANT TEST — Two Sum with HIGH S_final must STILL be not_applicable
    # This is the critical test: even if a linear problem is 100x slower than
    # the reference, it MUST NOT be classified as "inefficient" because
    # the output space for linear is {not_applicable} ONLY.
    r = compute_efficiency(
        traces=[{"execution_time": 0.01}],  # 10ms, S_final = 10/0.021 = 476!
        problem_key="Two Sum",
    )
    assert r.s_final > 100  # S_final is huge
    assert r.efficiency == "not_applicable"  # MUST still be not_applicable
    assert r.efficiency_applicable is False
    print(f"  Two Sum (HIGH S_final={r.s_final}): → {r.efficiency} (invariant holds) ✓")

    # Case 5: Unknown problem → not_applicable
    r = compute_efficiency(
        traces=[{"execution_time": 0.01}],
        problem_key="Unknown Problem",
    )
    assert r.s_ref_ms == 0.0
    assert r.efficiency == "not_applicable"
    assert r.efficiency_applicable is False
    print(f"  Unknown: S_final={r.s_final} → {r.efficiency} (no ref) ✓")

    # Case 6: Unknown s_kind with valid S_ref → not_applicable
    r = compute_efficiency(
        traces=[{"execution_time": 0.001}],
        problem_key="N-Queens",
        s_kind_override="weird_category",
    )
    assert r.efficiency == "not_applicable"
    assert r.efficiency_applicable is False
    print(f"  Unknown s_kind: → {r.efficiency} (unknown category) ✓")

    print("  All self-tests passed ✓")


if __name__ == "__main__":
    print("S-Efficiency Layer — Self Test (disjoint branches)")
    print("=" * 55)
    _self_test()
