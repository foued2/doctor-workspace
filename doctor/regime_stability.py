"""
Regime Stability Validation v1
===============================
Tests whether regime definitions are invariant under alternative valid classifiers.

Does NOT:
  - Improve coverage
  - Add new metrics
  - Change TEST_SUITES
  - Modify partition_power formula

Only tests:
  - Agreement between 3 independent regime classifiers
  - Detection of regime-dependent coverage inversions
  - Identification of unstable/phantom regimes
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set, Tuple

from doctor.ingestion import TestCaseSpec


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════

@dataclass
class ClassifierResult:
    """Result from one regime classifier for a single test."""
    test_label: str
    regime_id: str
    boundary_type: str
    is_edge: bool


@dataclass
class DisagreementPair:
    """A test where two classifiers disagree."""
    test_label: str
    classifier_a: str
    regime_a: str
    classifier_b: str
    regime_b: str
    coverage_inversion: bool  # "critical" under A but "redundant" under B


@dataclass
class StabilityReport:
    problem_id: str
    classifiers: List[str]
    pairwise_overlap: Dict[str, float]       # "A_vs_B" → Jaccard score
    disagreement_pairs: List[DisagreementPair]
    unstable_regimes: List[str]              # regimes that exist under only one classifier
    coverage_inversions: List[DisagreementPair]
    overall_stability: float                 # 0.0 = total disagreement, 1.0 = perfect


# ═══════════════════════════════════════════════════════════════
# CLASSIFIER A: Lexical (current system)
# ═══════════════════════════════════════════════════════════════

def classify_lexical(tc: TestCaseSpec, problem_id: str) -> ClassifierResult:
    """Current keyword-based regime classification from structural_partition.py.

    Extracts keywords from anchor names, matches against regime definition keywords.
    """
    regime_id = "unknown"
    boundary_type = "internal"
    is_edge = False

    for val_idx, val in enumerate(tc.input):
        if isinstance(val, list) and len(val) > 0:
            arr_len = len(val)
            int_vals = [v for v in val if isinstance(v, int) and not isinstance(v, bool)]

            has_negative = any(v < 0 for v in int_vals)
            has_positive = any(v > 0 for v in int_vals)
            all_same = len(set(int_vals)) == 1 if int_vals else False
            has_zero = any(v == 0 for v in int_vals)

            if problem_id in ("two_sum", "three_sum", "four_sum"):
                if arr_len <= 3:
                    regime_id = "array_min_length"
                    boundary_type = "min"
                    is_edge = True
                if has_negative and not has_positive:
                    regime_id = "values_all_negative"
                    is_edge = True
                if has_negative and has_positive:
                    regime_id = "values_mixed_sign"
                if all_same and arr_len > 1:
                    regime_id = "values_all_same"
                    boundary_type = "degenerate"
                    is_edge = True
                if int_vals == sorted(int_vals) and len(int_vals) > 2:
                    regime_id = "values_sorted"
                elif int_vals == sorted(int_vals, reverse=True) and len(int_vals) > 2:
                    regime_id = "values_reverse_sorted"
                elif len(int_vals) != len(set(int_vals)):
                    regime_id = "values_duplicate"

            elif problem_id in ("max_area", "trap"):
                if arr_len <= 3:
                    regime_id = "height_min_length"
                    boundary_type = "min"
                    is_edge = True
                if all_same:
                    regime_id = "height_all_equal"
                    boundary_type = "degenerate"
                    is_edge = True
                if has_zero:
                    regime_id = "height_zero_values"
                    is_edge = True

        elif isinstance(val, str):
            str_len = len(val)
            if problem_id == "valid_parentheses":
                if str_len == 0:
                    regime_id = "string_empty"
                    boundary_type = "degenerate"
                    is_edge = True
                elif str_len == 1:
                    regime_id = "string_length_one"
                    boundary_type = "min"
                    is_edge = True
                elif str_len == 2:
                    regime_id = "string_length_two"
                    boundary_type = "min"
                    is_edge = True
                else:
                    # Check balance
                    stack = []
                    mapping = {')': '(', ']': '[', '}': '{'}
                    balanced = True
                    for c in val:
                        if c in '([{':
                            stack.append(c)
                        elif c in ')]}':
                            if not stack or stack[-1] != mapping[c]:
                                balanced = False
                                break
                            stack.pop()
                    balanced = balanced and len(stack) == 0

                    if balanced:
                        bracket_types = set(c for c in val if c in '()[]{}')
                        if len(bracket_types) >= 6:
                            regime_id = "all_three_types"
                        elif len(bracket_types) >= 2:
                            regime_id = "balanced_simple"
                        else:
                            regime_id = "all_one_type"
                    else:
                        if '(' in val and ']' in val or '[' in val and ')' in val:
                            regime_id = "unbalanced_wrong_type"
                            boundary_type = "transition"
                            is_edge = True
                        elif str_len <= 4:
                            regime_id = "unbalanced_wrong_order"
                            boundary_type = "transition"
                            is_edge = True

        elif isinstance(val, int) and not isinstance(val, bool):
            if problem_id == "solve_n_queens":
                if val == 0:
                    regime_id = "n_zero"
                    boundary_type = "degenerate"
                    is_edge = True
                elif val == 1:
                    regime_id = "n_one"
                    boundary_type = "min"
                    is_edge = True
                elif val in (2, 3):
                    regime_id = "n_two_three"
                    boundary_type = "transition"
                    is_edge = True
                elif val == 4:
                    regime_id = "n_four"
                    boundary_type = "boundary"
                    is_edge = True
                elif 5 <= val <= 7:
                    regime_id = "n_medium"
                elif val >= 8:
                    regime_id = "n_large"
                    boundary_type = "max"
                    is_edge = True

    return ClassifierResult(
        test_label=tc.label,
        regime_id=regime_id,
        boundary_type=boundary_type,
        is_edge=is_edge,
    )


# ═══════════════════════════════════════════════════════════════
# CLASSIFIER B: Constraint-Rule Based
# ═══════════════════════════════════════════════════════════════

def classify_constraint_rules(tc: TestCaseSpec, problem_id: str,
                                constraints: Dict[str, Any]) -> ClassifierResult:
    """Manual parsing of problem spec constraints.

    Uses only the constraint definitions to classify tests.
    No keyword matching — direct constraint evaluation.
    """
    regime_id = "constraint_interior"
    boundary_type = "internal"
    is_edge = False

    for val_idx, val in enumerate(tc.input):
        if isinstance(val, list) and len(val) > 0:
            arr_len = len(val)
            for cname, cval in constraints.items():
                if isinstance(cval, dict):
                    if "min_length" in cval and arr_len == cval["min_length"]:
                        regime_id = f"constraint_{cname}_at_min"
                        boundary_type = "min"
                        is_edge = True
                    elif "min_length" in cval and arr_len < cval["min_length"] + 3:
                        regime_id = f"constraint_{cname}_near_min"
                        boundary_type = "min"
                        is_edge = True
                    elif "min" in cval and any(isinstance(v, int) and v == cval["min"] for v in val if isinstance(v, int)):
                        regime_id = f"constraint_{cname}_value_at_min"
                        boundary_type = "min"
                        is_edge = True
                    elif "max" in cval and any(isinstance(v, int) and v == cval["max"] for v in val if isinstance(v, int)):
                        regime_id = f"constraint_{cname}_value_at_max"
                        boundary_type = "max"
                        is_edge = True

        elif isinstance(val, str):
            str_len = len(val)
            for cname, cval in constraints.items():
                if isinstance(cval, dict):
                    if "min_length" in cval and str_len == cval["min_length"]:
                        regime_id = f"constraint_{cname}_at_min"
                        boundary_type = "min"
                        is_edge = True
                    elif "min_length" in cval and str_len == 0:
                        regime_id = f"constraint_{cname}_degenerate"
                        boundary_type = "degenerate"
                        is_edge = True

        elif isinstance(val, int) and not isinstance(val, bool):
            for cname, cval in constraints.items():
                if isinstance(cval, dict):
                    if "min" in cval and val == cval["min"]:
                        regime_id = f"constraint_{cname}_at_min"
                        boundary_type = "min"
                        is_edge = True
                    elif "max" in cval and val == cval["max"]:
                        regime_id = f"constraint_{cname}_at_max"
                        boundary_type = "max"
                        is_edge = True
                    elif val == 0:
                        regime_id = f"constraint_{cname}_zero"
                        boundary_type = "degenerate"
                        is_edge = True
                    elif val == 1:
                        regime_id = f"constraint_{cname}_unit"
                        boundary_type = "min"
                        is_edge = True

    return ClassifierResult(
        test_label=tc.label,
        regime_id=regime_id,
        boundary_type=boundary_type,
        is_edge=is_edge,
    )


# ═══════════════════════════════════════════════════════════════
# CLASSIFIER C: Structural Heuristic
# ═══════════════════════════════════════════════════════════════

def classify_structural_heuristic(tc: TestCaseSpec, problem_id: str) -> ClassifierResult:
    """Input-shape based classification only.

    No keywords, no constraints — purely structural properties of input:
    - size (small/medium/large)
    - homogeneity (uniform/diverse)
    - ordering (sorted/reverse/random)
    - complexity (simple/nested/mixed)
    """
    regime_id = "structural_interior"
    boundary_type = "internal"
    is_edge = False

    for val_idx, val in enumerate(tc.input):
        if isinstance(val, list) and len(val) > 0:
            arr_len = len(val)
            unique_count = len(set(str(v) for v in val))
            diversity_ratio = unique_count / arr_len if arr_len > 0 else 0

            # Size classification
            if arr_len <= 2:
                regime_id = "structural_tiny"
                boundary_type = "min"
                is_edge = True
            elif arr_len <= 4:
                regime_id = "structural_small"
                boundary_type = "min"
            elif arr_len <= 10:
                regime_id = "structural_medium"
            else:
                regime_id = "structural_large"
                boundary_type = "max"

            # Homogeneity
            if diversity_ratio == 0:
                regime_id = "structural_uniform"
                boundary_type = "degenerate"
                is_edge = True
            elif diversity_ratio < 0.5:
                regime_id = "structural_low_diversity"

            # Ordering
            int_vals = [v for v in val if isinstance(v, int) and not isinstance(v, bool)]
            if len(int_vals) > 2:
                if int_vals == sorted(int_vals):
                    regime_id = "structural_sorted_asc"
                elif int_vals == sorted(int_vals, reverse=True):
                    regime_id = "structural_sorted_desc"

        elif isinstance(val, str):
            str_len = len(val)
            unique_chars = len(set(val))
            char_diversity = unique_chars / str_len if str_len > 0 else 0

            if str_len == 0:
                regime_id = "structural_empty"
                boundary_type = "degenerate"
                is_edge = True
            elif str_len <= 2:
                regime_id = "structural_tiny_string"
                boundary_type = "min"
                is_edge = True
            elif str_len <= 6:
                regime_id = "structural_short_string"
            elif char_diversity < 0.3:
                regime_id = "structural_repetitive_string"
            else:
                regime_id = "structural_diverse_string"

        elif isinstance(val, int) and not isinstance(val, bool):
            if val == 0:
                regime_id = "structural_zero"
                boundary_type = "degenerate"
                is_edge = True
            elif val == 1:
                regime_id = "structural_unit"
                boundary_type = "min"
                is_edge = True
            elif val < 0:
                regime_id = "structural_negative"
                boundary_type = "min"
            elif val >= 100:
                regime_id = "structural_large_scalar"
                boundary_type = "max"

    return ClassifierResult(
        test_label=tc.label,
        regime_id=regime_id,
        boundary_type=boundary_type,
        is_edge=is_edge,
    )


# ═══════════════════════════════════════════════════════════════
# AGREEMENT COMPUTATION
# ═══════════════════════════════════════════════════════════════

def jaccard(set_a: Set[str], set_b: Set[str]) -> float:
    """Jaccard similarity between two sets of regime IDs."""
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union > 0 else 0.0


def compute_stability(
    problem_id: str,
    test_cases: List[TestCaseSpec],
    constraints: Dict[str, Any],
) -> StabilityReport:
    """Run all 3 classifiers and compute stability metrics."""
    classifiers = ["lexical", "constraint_rules", "structural_heuristic"]

    # Run all classifiers
    results_a = [classify_lexical(tc, problem_id) for tc in test_cases]
    results_b = [classify_constraint_rules(tc, problem_id, constraints) for tc in test_cases]
    results_c = [classify_structural_heuristic(tc, problem_id) for tc in test_cases]

    all_results = {
        "lexical": results_a,
        "constraint_rules": results_b,
        "structural_heuristic": results_c,
    }

    # Regime sets per classifier
    regime_sets = {
        name: set(r.regime_id for r in results)
        for name, results in all_results.items()
    }

    # Pairwise Jaccard overlap
    pairwise_overlap = {}
    for i, name_a in enumerate(classifiers):
        for j, name_b in enumerate(classifiers):
            if i < j:
                key = f"{name_a}_vs_{name_b}"
                pairwise_overlap[key] = jaccard(regime_sets[name_a], regime_sets[name_b])

    # Per-test disagreement detection
    disagreement_pairs = []
    coverage_inversions = []

    # Compute regime counts per classifier (for redundancy detection)
    regime_counts = {}
    for name, results in all_results.items():
        counts = {}
        for r in results:
            counts[r.regime_id] = counts.get(r.regime_id, 0) + 1
        regime_counts[name] = counts

    for idx, tc in enumerate(test_cases):
        ra = results_a[idx]
        rb = results_b[idx]
        rc = results_c[idx]

        # Lexical vs Constraint
        if ra.regime_id != rb.regime_id:
            # Check for coverage inversion: is it "critical" (unique) under one but "redundant" under other?
            count_a = regime_counts["lexical"].get(ra.regime_id, 1)
            count_b = regime_counts["constraint_rules"].get(rb.regime_id, 1)
            is_inversion = (count_a == 1 and count_b > 1) or (count_b == 1 and count_a > 1)

            dp = DisagreementPair(
                test_label=tc.label,
                classifier_a="lexical",
                regime_a=ra.regime_id,
                classifier_b="constraint_rules",
                regime_b=rb.regime_id,
                coverage_inversion=is_inversion,
            )
            disagreement_pairs.append(dp)
            if is_inversion:
                coverage_inversions.append(dp)

        # Lexical vs Structural
        if ra.regime_id != rc.regime_id:
            count_a = regime_counts["lexical"].get(ra.regime_id, 1)
            count_c = regime_counts["structural_heuristic"].get(rc.regime_id, 1)
            is_inversion = (count_a == 1 and count_c > 1) or (count_c == 1 and count_a > 1)

            dp = DisagreementPair(
                test_label=tc.label,
                classifier_a="lexical",
                regime_a=ra.regime_id,
                classifier_b="structural_heuristic",
                regime_b=rc.regime_id,
                coverage_inversion=is_inversion,
            )
            disagreement_pairs.append(dp)
            if is_inversion:
                coverage_inversions.append(dp)

        # Constraint vs Structural
        if rb.regime_id != rc.regime_id:
            count_b = regime_counts["constraint_rules"].get(rb.regime_id, 1)
            count_c = regime_counts["structural_heuristic"].get(rc.regime_id, 1)
            is_inversion = (count_b == 1 and count_c > 1) or (count_c == 1 and count_b > 1)

            dp = DisagreementPair(
                test_label=tc.label,
                classifier_a="constraint_rules",
                regime_a=rb.regime_id,
                classifier_b="structural_heuristic",
                regime_b=rc.regime_id,
                coverage_inversion=is_inversion,
            )
            disagreement_pairs.append(dp)
            if is_inversion:
                coverage_inversions.append(dp)

    # Unstable regimes: exist under only one classifier
    all_regimes = regime_sets["lexical"] | regime_sets["constraint_rules"] | regime_sets["structural_heuristic"]
    unstable_regimes = []
    for reg in all_regimes:
        present_in = sum(1 for name in classifiers if reg in regime_sets[name])
        if present_in == 1:
            unstable_regimes.append(reg)

    # Overall stability: average pairwise Jaccard
    if pairwise_overlap:
        overall_stability = sum(pairwise_overlap.values()) / len(pairwise_overlap)
    else:
        overall_stability = 1.0

    return StabilityReport(
        problem_id=problem_id,
        classifiers=classifiers,
        pairwise_overlap=pairwise_overlap,
        disagreement_pairs=disagreement_pairs,
        unstable_regimes=unstable_regimes,
        coverage_inversions=coverage_inversions,
        overall_stability=round(overall_stability, 3),
    )


# ═══════════════════════════════════════════════════════════════
# REPORT FORMATTING
# ═══════════════════════════════════════════════════════════════

def format_stability_report(report: StabilityReport) -> str:
    """Human-readable stability report."""
    lines = []
    lines.append("=" * 65)
    lines.append(f"REGIME STABILITY VALIDATION: {report.problem_id}")
    lines.append("=" * 65)
    lines.append(f"Classifiers: {', '.join(report.classifiers)}")
    lines.append(f"Overall stability: {report.overall_stability:.3f}")
    lines.append(f"Total disagreements: {len(report.disagreement_pairs)}")
    lines.append(f"Coverage inversions: {len(report.coverage_inversions)}")
    lines.append(f"Unstable regimes: {len(report.unstable_regimes)}")
    lines.append("")

    lines.append("PAIRWISE JACCARD OVERLAP:")
    for key, score in report.pairwise_overlap.items():
        status = "✓" if score >= 0.5 else "⚠" if score >= 0.2 else "✗"
        lines.append(f"  {status} {key}: {score:.3f}")
    lines.append("")

    if report.unstable_regimes:
        lines.append("UNSTABLE REGIMES (exist under only one classifier):")
        for reg in report.unstable_regimes:
            lines.append(f"  ~ {reg}")
        lines.append("")

    if report.disagreement_pairs:
        lines.append("DISAGREEMENT PAIRS (first 10):")
        for dp in report.disagreement_pairs[:10]:
            inv = " [COVERAGE INVERSION]" if dp.coverage_inversion else ""
            lines.append(f"  {dp.test_label}:")
            lines.append(f"    {dp.classifier_a}: {dp.regime_a}")
            lines.append(f"    {dp.classifier_b}: {dp.regime_b}{inv}")
        lines.append("")

    if report.coverage_inversions:
        lines.append(f"COVERAGE INVERSIONS ({len(report.coverage_inversions)}):")
        for dp in report.coverage_inversions:
            lines.append(f"  {dp.test_label}:")
            lines.append(f"    Critical under {dp.classifier_a} ({dp.regime_a}), "
                        f"redundant under {dp.classifier_b} ({dp.regime_b})")
        lines.append("")

    return "\n".join(lines)
