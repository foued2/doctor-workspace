"""Evidence Score — Test-based coverage strength estimator.

Computes a continuous score from discrete test outcomes.
This is NOT a belief estimate. NOT probability of correctness.
This is a measure of how thoroughly the solution has been tested.

Derived from:
  - tests_passed / tests_total (pass rate)
  - tests_total (coverage depth)
  - has_edge_cases (coverage breadth)

Rules:
  - tests_total < 3: score <= 0.5 regardless of pass rate
  - tests_total >= 3 and pass_rate = 1.0: score max 0.85
  - tests_total >= 6 and pass_rate = 1.0 and has_edge_cases: score max 0.95

Do NOT interpret this as confidence or belief.
"""
from __future__ import annotations


def compute_evidence_score(
    tests_passed: int,
    tests_total: int,
    has_edge_cases: bool = False,
) -> float:
    """Compute evidence score from test execution results.

    This is a measure of test coverage strength, NOT a belief estimate.
    Do not interpret as probability of correctness.

    Args:
        tests_passed: Number of tests that passed.
        tests_total: Total number of tests executed.
        has_edge_cases: Whether the test suite includes edge-case tests.

    Returns:
        Evidence score in [0.0, 1.0].
    """
    if tests_total <= 0:
        return 0.0

    pass_rate = tests_passed / tests_total

    # No tests or all failed → zero confidence
    if pass_rate == 0.0:
        return 0.0

    # ── Tier 1: Thin coverage (< 3 tests) ──────────────────────────
    if tests_total < 3:
        # Cap at 0.5 even if all pass — too few to be sure
        raw = pass_rate * 0.5
        return round(min(raw, 0.5), 2)

    # ── Tier 2: Moderate coverage (3-5 tests) ──────────────────────
    if tests_total < 6:
        # Perfect pass rate can reach 0.85 max
        max_conf = 0.85
        raw = pass_rate * max_conf
        return round(min(raw, max_conf), 2)

    # ── Tier 3: Rich coverage (6+ tests) ───────────────────────────
    if has_edge_cases:
        # Full suite with edge cases: can reach 0.95
        max_conf = 0.95
    else:
        # No edge-case coverage: cap at 0.85 even with many tests
        max_conf = 0.85

    raw = pass_rate * max_conf
    return round(min(raw, max_conf), 2)
