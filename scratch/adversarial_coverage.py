"""
Solution-Space Sensitivity Model v1
=====================================
Measures TEST_SUITES quality via ΔE sensitivity analysis.

PRINCIPLE: The pipeline evaluates test structure, NOT solution correctness.

Uses:
  - Input mutation (deterministic)
  - Reference function evaluation (single-source, human-approved)
  - ΔE sensitivity computation (change in expected output)
  - Structural coverage metrics (semantic, per problem class)

Does NOT use:
  - Runtime solution evaluation
  - Multi-solution voting
  - Heuristic expected-output inference
  - Historical failure data
"""
from __future__ import annotations

import hashlib
import statistics
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from doctor.ingestion import ProblemSpec, TestCaseSpec


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════

@dataclass
class MutationResult:
    """Result of mutating one input."""
    original_input: tuple
    mutated_input: tuple
    mutation_axis: str
    original_expected: Any
    mutated_expected: Any
    delta_nonzero: bool          # True if E changed
    delta_magnitude: float       # numeric distance between outputs (0 if not numeric)


@dataclass
class TestSensitivity:
    """Sensitivity profile for one test case."""
    test_case: TestCaseSpec
    total_mutations: int
    mutations_causing_delta: int   # count where ΔE != 0
    sensitivity_ratio: float       # mutations_causing_delta / total_mutations
    mutation_details: List[MutationResult]
    is_low_discrimination: bool    # True if sensitivity_ratio < threshold


@dataclass
class CoverageGap:
    """A structural gap in the test suite."""
    gap_type: str                  # "size", "range", "boundary", "redundancy"
    description: str
    severity: str                  # "high" | "medium" | "low"
    recommendation: str            # what to generate to fill the gap


@dataclass
class SensitivityReport:
    """Full sensitivity analysis for one problem."""
    problem_id: str
    test_sensitivities: List[TestSensitivity]
    coverage_gaps: List[CoverageGap]
    low_discrimination_tests: List[str]   # labels of weak tests
    redundancy_clusters: List[List[str]]  # groups of tests with similar inputs
    boundary_density: Dict[str, int]      # count of tests at each constraint boundary
    avg_sensitivity: float         # mean sensitivity_ratio across all tests


# ═══════════════════════════════════════════════════════════════
# MUTATION AXES (per problem class)
# ═══════════════════════════════════════════════════════════════

class MutationEngine:
    """Generates deterministic input mutations for sensitivity analysis."""

    # ── Array mutations ──────────────────────────────────────
    @staticmethod
    def mutate_array_duplicate_inject(arr: list, value: int, positions: list[int]) -> list:
        """Inject duplicate values at specified positions."""
        result = list(arr)
        for p in positions:
            if 0 <= p < len(result):
                result[p] = value
        return result

    @staticmethod
    def mutate_array_reverse(arr: list) -> list:
        """Reverse the array."""
        return list(reversed(arr))

    @staticmethod
    def mutate_array_single_element(arr: list, index: int, value: Any) -> list:
        """Change one element to a different value."""
        result = list(arr)
        if 0 <= index < len(result):
            result[index] = value
        return result

    @staticmethod
    def mutate_array_all_same(arr: list, value: Any) -> list:
        """Set all elements to the same value."""
        return [value] * len(arr)

    @staticmethod
    def mutate_array_sort(arr: list, reverse: bool = False) -> list:
        """Sort the array."""
        try:
            return sorted(arr, reverse=reverse)
        except TypeError:
            return list(arr)

    @staticmethod
    def mutate_array_shrink(arr: list, size: int) -> list:
        """Shrink array to first N elements."""
        return list(arr[:size])

    @staticmethod
    def mutate_array_extend(arr: list, value: Any, count: int) -> list:
        """Extend array with repeated values."""
        return list(arr) + [value] * count

    # ── String mutations ─────────────────────────────────────
    @staticmethod
    def mutate_string_repeat(s: str, char: str, count: int) -> str:
        """Replace string with repeated character."""
        return char * count

    @staticmethod
    def mutate_string_truncate(s: str, length: int) -> str:
        """Truncate string to length."""
        return s[:length]

    @staticmethod
    def mutate_string_reverse(s: str) -> str:
        """Reverse the string."""
        return s[::-1]

    @staticmethod
    def mutate_string_insert(s: str, index: int, text: str) -> str:
        """Insert text at position."""
        return s[:index] + text + s[index:]

    # ── Numeric mutations ────────────────────────────────────
    @staticmethod
    def mutate_numeric_sign(val: int) -> int:
        """Flip the sign."""
        return -val

    @staticmethod
    def mutate_numeric_boundary(val: int, boundary: int) -> int:
        """Replace with boundary value."""
        return boundary

    @staticmethod
    def mutate_numeric_zero(val: Any) -> Any:
        """Replace with zero."""
        if isinstance(val, int):
            return 0
        return val

    # ── Linked list mutations ────────────────────────────────
    @staticmethod
    def mutate_listnode_extend(head, count: int, value: int):
        """Extend linked list with N nodes."""
        try:
            from doctor.test_executor import ListNode
        except ImportError:
            return head
        if head is None and count > 0:
            head = ListNode(value)
            curr = head
            for _ in range(count - 1):
                curr.next = ListNode(value)
                curr = curr.next
            return head
        # Append to end
        curr = head
        while curr and curr.next:
            curr = curr.next
        if curr:
            for _ in range(count):
                curr.next = ListNode(value)
                curr = curr.next
        return head


# ═══════════════════════════════════════════════════════════════
# ΔE COMPUTATION
# ═══════════════════════════════════════════════════════════════

def compute_delta(expected_original: Any, expected_mutated: Any) -> Tuple[bool, float]:
    """Compute whether expected output changed, and by how much.

    Returns (delta_nonzero, delta_magnitude).
    Magnitude is 0 for non-numeric outputs, or the numeric distance.
    """
    if expected_original == expected_mutated:
        return False, 0.0

    # Numeric distance
    if isinstance(expected_original, (int, float)) and isinstance(expected_mutated, (int, float)):
        return True, abs(expected_mutated - expected_original)

    # String distance (length difference)
    if isinstance(expected_original, str) and isinstance(expected_mutated, str):
        return True, float(abs(len(expected_mutated) - len(expected_original)))

    # List distance (length + element count difference)
    if isinstance(expected_original, list) and isinstance(expected_mutated, list):
        len_diff = abs(len(expected_mutated) - len(expected_original))
        elem_diff = sum(1 for a, b in zip(sorted(map(str, expected_original)),
                                           sorted(map(str, expected_mutated))) if a != b)
        return True, float(len_diff + elem_diff)

    # Boolean / other: any change is a delta
    return True, 1.0


# ═══════════════════════════════════════════════════════════════
# SENSITIVITY ANALYSIS
# ═══════════════════════════════════════════════════════════════

def analyze_test_sensitivity(
    test_case: TestCaseSpec,
    reference_fn: Callable,
    constraints: Dict[str, Any],
    mutation_count: int = 10,
    low_discrimination_threshold: float = 0.30,
) -> TestSensitivity:
    """Analyze how sensitive one test case is to input mutations.

    Method:
      1. Apply mutation axes to test_case.input
      2. Compute E_original = reference(original_input)
      3. Compute E_mutated = reference(mutated_input)
      4. Compute ΔE = |E_mutated - E_original|
      5. sensitivity_ratio = count(ΔE != 0) / total_mutations

    A test with low sensitivity_ratio is in a "flat region" —
    many different inputs produce the same output, making it
    easy for wrong solutions to pass.
    """
    mutations = _generate_mutations(test_case.input, constraints, reference_fn, mutation_count)

    E_original = reference_fn(*test_case.input)

    mutation_results = []
    delta_count = 0

    for mut in mutations:
        try:
            E_mutated = reference_fn(*mut.mutated_input)
        except Exception:
            E_mutated = None

        delta_nonzero, delta_mag = compute_delta(E_original, E_mutated)
        if delta_nonzero:
            delta_count += 1

        mutation_results.append(MutationResult(
            original_input=test_case.input,
            mutated_input=mut.mutated_input,
            mutation_axis=mut.mutation_axis,
            original_expected=E_original,
            mutated_expected=E_mutated,
            delta_nonzero=delta_nonzero,
            delta_magnitude=delta_mag,
        ))

    total = len(mutation_results)
    sensitivity = delta_count / total if total > 0 else 0.0

    return TestSensitivity(
        test_case=test_case,
        total_mutations=total,
        mutations_causing_delta=delta_count,
        sensitivity_ratio=round(sensitivity, 3),
        mutation_details=mutation_results,
        is_low_discrimination=sensitivity < low_discrimination_threshold,
    )


def _generate_mutations(
    original_input: tuple,
    constraints: Dict[str, Any],
    reference_fn: Callable,
    count: int,
) -> List[MutationResult]:
    """Generate a deterministic set of mutations for an input tuple."""
    mutations = []
    me = MutationEngine()

    for i, val in enumerate(original_input):
        # Array mutations
        if isinstance(val, list) and len(val) > 0:
            # Duplicate injection
            dup_val = val[0] if val else 0
            dup_pos = list(range(min(2, len(val))))
            mutated = me.mutate_array_duplicate_inject(val, dup_val, dup_pos)
            mutations.append(MutationResult(
                original_input=original_input,
                mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                mutation_axis="duplicate_inject",
                original_expected=None, mutated_expected=None,
                delta_nonzero=False, delta_magnitude=0.0,
            ))

            # Reverse
            mutated = me.mutate_array_reverse(val)
            mutations.append(MutationResult(
                original_input=original_input,
                mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                mutation_axis="reverse",
                original_expected=None, mutated_expected=None,
                delta_nonzero=False, delta_magnitude=0.0,
            ))

            # Sort ascending
            mutated = me.mutate_array_sort(val)
            mutations.append(MutationResult(
                original_input=original_input,
                mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                mutation_axis="sort_asc",
                original_expected=None, mutated_expected=None,
                delta_nonzero=False, delta_magnitude=0.0,
            ))

            # Sort descending
            mutated = me.mutate_array_sort(val, reverse=True)
            mutations.append(MutationResult(
                original_input=original_input,
                mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                mutation_axis="sort_desc",
                original_expected=None, mutated_expected=None,
                delta_nonzero=False, delta_magnitude=0.0,
            ))

            # All same
            mutated = me.mutate_array_all_same(val, val[0] if val else 0)
            mutations.append(MutationResult(
                original_input=original_input,
                mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                mutation_axis="all_same",
                original_expected=None, mutated_expected=None,
                delta_nonzero=False, delta_magnitude=0.0,
            ))

            # Shrink to min length
            if len(val) > 2:
                mutated = me.mutate_array_shrink(val, 2)
                mutations.append(MutationResult(
                    original_input=original_input,
                    mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                    mutation_axis="shrink_min",
                    original_expected=None, mutated_expected=None,
                    delta_nonzero=False, delta_magnitude=0.0,
                ))

            # Single element change
            mutated = me.mutate_array_single_element(val, 0, val[0] + 1 if val else 1)
            mutations.append(MutationResult(
                original_input=original_input,
                mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                mutation_axis="single_element_change",
                original_expected=None, mutated_expected=None,
                delta_nonzero=False, delta_magnitude=0.0,
            ))

        # String mutations
        if isinstance(val, str):
            mutated = me.mutate_string_reverse(val)
            mutations.append(MutationResult(
                original_input=original_input,
                mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                mutation_axis="string_reverse",
                original_expected=None, mutated_expected=None,
                delta_nonzero=False, delta_magnitude=0.0,
            ))

            mutated = me.mutate_string_truncate(val, max(1, len(val) // 2))
            mutations.append(MutationResult(
                original_input=original_input,
                mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                mutation_axis="truncate_half",
                original_expected=None, mutated_expected=None,
                delta_nonzero=False, delta_magnitude=0.0,
            ))

        # Numeric mutations
        if isinstance(val, int) and not isinstance(val, bool):
            mutated_val = me.mutate_numeric_sign(val)
            mutated = mutated_val
            mutations.append(MutationResult(
                original_input=original_input,
                mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                mutation_axis="sign_flip",
                original_expected=None, mutated_expected=None,
                delta_nonzero=False, delta_magnitude=0.0,
            ))

            mutated_val = me.mutate_numeric_zero(val)
            mutated = mutated_val
            mutations.append(MutationResult(
                original_input=original_input,
                mutated_input=tuple(original_input[:i] + (mutated,) + original_input[i+1:]),
                mutation_axis="zero",
                original_expected=None, mutated_expected=None,
                delta_nonzero=False, delta_magnitude=0.0,
            ))

    return mutations[:count] if count < len(mutations) else mutations


# ═══════════════════════════════════════════════════════════════
# STRUCTURAL COVERAGE
# ═══════════════════════════════════════════════════════════════

def compute_structural_coverage(
    test_cases: List[TestCaseSpec],
    constraints: Dict[str, Any],
) -> Dict[str, Any]:
    """Compute semantic structural coverage of a test suite.

    Metrics:
      - input_size_distribution: range of input sizes covered
      - value_range: min/max values seen in inputs
      - label_diversity: unique test labels
      - boundary_coverage: how many constraint boundaries are tested
    """
    sizes = []
    values = []
    labels = set()
    boundary_hits = {"min": 0, "max": 0, "zero": 0, "negative": 0, "positive": 0}

    for tc in test_cases:
        for val in tc.input:
            if isinstance(val, list):
                sizes.append(len(val))
                for v in val:
                    if isinstance(v, (int, float)) and not isinstance(v, bool):
                        values.append(v)
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                values.append(val)
            elif isinstance(val, str):
                sizes.append(len(val))

        labels.add(tc.label)

        # Check boundary hits
        for val in tc.input:
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                if val == 0:
                    boundary_hits["zero"] += 1
                if val < 0:
                    boundary_hits["negative"] += 1
                if val > 0:
                    boundary_hits["positive"] += 1

    # Check min/max constraint hits
    for cname, cval in constraints.items():
        if isinstance(cval, dict):
            if "min_length" in cval:
                if cval["min_length"] in sizes:
                    boundary_hits["min"] += 1
            if "min" in cval:
                if cval["min"] in values:
                    boundary_hits["min"] += 1
            if "max" in cval:
                if cval["max"] in values:
                    boundary_hits["max"] += 1

    return {
        "input_sizes": sorted(set(sizes)),
        "input_size_range": (min(sizes), max(sizes)) if sizes else (0, 0),
        "value_range": (min(values), max(values)) if values else (0, 0),
        "label_diversity": sorted(labels),
        "label_count": len(labels),
        "boundary_coverage": boundary_hits,
        "test_count": len(test_cases),
    }


# ═══════════════════════════════════════════════════════════════
# COVERAGE GAP DETECTION
# ═══════════════════════════════════════════════════════════════

def detect_coverage_gaps(
    test_cases: List[TestCaseSpec],
    constraints: Dict[str, Any],
    coverage: Dict[str, Any],
) -> List[CoverageGap]:
    """Detect structural gaps in the test suite."""
    gaps = []

    # Gap 1: Insufficient size diversity
    sizes = coverage["input_sizes"]
    if len(sizes) < 4:
        gaps.append(CoverageGap(
            gap_type="size",
            description=f"Only {len(sizes)} distinct input sizes tested: {sizes}",
            severity="medium",
            recommendation="Add test cases with more varied input sizes",
        ))

    # Gap 2: No boundary coverage
    bc = coverage["boundary_coverage"]
    if bc["zero"] == 0:
        gaps.append(CoverageGap(
            gap_type="boundary",
            description="No test cases with zero values",
            severity="low",
            recommendation="Add test case with zero input",
        ))
    if bc["negative"] == 0 and any(isinstance(cval, dict) and "min" in cval and cval["min"] < 0 for cval in constraints.values()):
        gaps.append(CoverageGap(
            gap_type="boundary",
            description="No test cases with negative values (constraint allows negatives)",
            severity="medium",
            recommendation="Add test case with negative input",
        ))

    # Gap 3: Redundancy (tests with identical or near-identical inputs)
    input_strings = [str(tc.input) for tc in test_cases]
    seen = {}
    for i, s in enumerate(input_strings):
        if s in seen:
            gaps.append(CoverageGap(
                gap_type="redundancy",
                description=f"Test '{test_cases[i].label}' has same input as '{test_cases[seen[s]].label}'",
                severity="low",
                recommendation="Remove duplicate or differentiate inputs",
            ))
        else:
            seen[s] = i

    # Gap 4: Constraint boundaries not tested
    for cname, cval in constraints.items():
        if isinstance(cval, dict):
            if "max" in cval:
                max_val = cval["max"]
                if max_val not in [v for tc in test_cases for v in tc.input if isinstance(v, (int, float))]:
                    gaps.append(CoverageGap(
                        gap_type="boundary",
                        description=f"Constraint max ({cname}={max_val}) not tested",
                        severity="low",
                        recommendation=f"Add test case with {cname}={max_val}",
                    ))

    return gaps


# ═══════════════════════════════════════════════════════════════
# REDUNDANCY CLUSTERING
# ═══════════════════════════════════════════════════════════════

def detect_redundancy_clusters(
    test_cases: List[TestCaseSpec],
    similarity_threshold: float = 0.80,
) -> List[List[str]]:
    """Group tests with structurally similar inputs.

    Similarity = ratio of matching input elements.
    """
    clusters: List[List[str]] = []
    assigned = set()

    for i, tc_i in enumerate(test_cases):
        if i in assigned:
            continue
        cluster = [tc_i.label]
        for j, tc_j in enumerate(test_cases):
            if j <= i or j in assigned:
                continue
            sim = _input_similarity(tc_i.input, tc_j.input)
            if sim >= similarity_threshold:
                cluster.append(tc_j.label)
                assigned.add(j)
        if len(cluster) > 1:
            clusters.append(cluster)
        assigned.add(i)

    return clusters


def _input_similarity(input_a: tuple, input_b: tuple) -> float:
    """Compute structural similarity between two inputs."""
    if len(input_a) != len(input_b):
        return 0.0

    matches = 0
    total = 0
    for a, b in zip(input_a, input_b):
        if isinstance(a, list) and isinstance(b, list):
            total += max(len(a), len(b))
            matches += sum(1 for x, y in zip(a, b) if x == y)
        else:
            total += 1
            if a == b:
                matches += 1

    return matches / total if total > 0 else 0.0


# ═══════════════════════════════════════════════════════════════
# MAIN SENSITIVITY REPORT
# ═══════════════════════════════════════════════════════════════

def generate_sensitivity_report(
    problem_id: str,
    test_cases: List[TestCaseSpec],
    reference_fn: Callable,
    constraints: Dict[str, Any],
    mutation_count: int = 10,
) -> SensitivityReport:
    """Generate full sensitivity analysis for one problem.

    This is the entry point for the coverage audit workflow.
    """
    # Per-test sensitivity
    test_sensitivities = []
    for tc in test_cases:
        sensitivity = analyze_test_sensitivity(tc, reference_fn, constraints, mutation_count)
        test_sensitivities.append(sensitivity)

    # Structural coverage
    coverage = compute_structural_coverage(test_cases, constraints)

    # Coverage gaps
    gaps = detect_coverage_gaps(test_cases, constraints, coverage)

    # Low discrimination tests
    low_disc = [
        ts.test_case.label for ts in test_sensitivities if ts.is_low_discrimination
    ]

    # Redundancy clusters
    clusters = detect_redundancy_clusters(test_cases)

    # Average sensitivity
    avg_sens = (
        statistics.mean(ts.sensitivity_ratio for ts in test_sensitivities)
        if test_sensitivities else 0.0
    )

    # Boundary density
    boundary_density = coverage["boundary_coverage"]

    return SensitivityReport(
        problem_id=problem_id,
        test_sensitivities=test_sensitivities,
        coverage_gaps=gaps,
        low_discrimination_tests=low_disc,
        redundancy_clusters=clusters,
        boundary_density=boundary_density,
        avg_sensitivity=round(avg_sens, 3),
    )


# ═══════════════════════════════════════════════════════════════
# REPORT FORMATTING
# ═══════════════════════════════════════════════════════════════

def format_report(report: SensitivityReport) -> str:
    """Human-readable summary of sensitivity report."""
    lines = []
    lines.append(f"=" * 65)
    lines.append(f"SENSITIVITY REPORT: {report.problem_id}")
    lines.append(f"=" * 65)
    lines.append(f"Tests analyzed: {len(report.test_sensitivities)}")
    lines.append(f"Average sensitivity: {report.avg_sensitivity:.3f}")
    lines.append(f"Low discrimination tests: {len(report.low_discrimination_tests)}")
    lines.append(f"Coverage gaps: {len(report.coverage_gaps)}")
    lines.append(f"Redundancy clusters: {len(report.redundancy_clusters)}")
    lines.append("")

    if report.low_discrimination_tests:
        lines.append("LOW DISCRIMINATION TESTS (may be too easy):")
        for label in report.low_discrimination_tests:
            ts = next(t for t in report.test_sensitivities if t.test_case.label == label)
            lines.append(f"  {label}: sensitivity={ts.sensitivity_ratio:.3f}, "
                        f"{ts.mutations_causing_delta}/{ts.total_mutations} mutations caused ΔE")
        lines.append("")

    if report.coverage_gaps:
        lines.append("COVERAGE GAPS:")
        for gap in report.coverage_gaps:
            lines.append(f"  [{gap.severity.upper()}] {gap.gap_type}: {gap.description}")
            lines.append(f"    → {gap.recommendation}")
        lines.append("")

    if report.redundancy_clusters:
        lines.append("REDUNDANCY CLUSTERS:")
        for cluster in report.redundancy_clusters:
            lines.append(f"  {cluster}")
        lines.append("")

    # Per-test detail
    lines.append("PER-TEST SENSITIVITY:")
    for ts in report.test_sensitivities:
        flag = " ⚠ LOW" if ts.is_low_discrimination else ""
        lines.append(f"  {ts.test_case.label}: sensitivity={ts.sensitivity_ratio:.3f}{flag}")

    return "\n".join(lines)
