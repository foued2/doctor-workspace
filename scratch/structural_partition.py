"""
Structural Partition Audit v2
==============================
Replaces ΔE sensitivity with input-space partition analysis.

PRINCIPLE: Tests are input-space partition markers, not output validators.

A test's quality is measured by:
  - Which constraint regime it targets
  - How close it sits to a decision boundary
  - How much overlap it has with other tests in the same regime

NOT measured by:
  - How much the output changes under mutation
  - Whether the reference function produces different outputs
  - Any simulation of solution correctness
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from doctor.ingestion import TestCaseSpec


# ═══════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════

@dataclass
class ConstraintAnchor:
    """What rule/constraint this test exercises."""
    name: str                          # e.g., "nums.min_length", "target.zero"
    category: str                      # "boundary" | "interior" | "transition" | "degenerate"
    constraint_path: str               # dotted path to the constraint definition


@dataclass
class RegimeMapping:
    """Which input equivalence class this test targets."""
    regime_id: str                     # e.g., "array_positive_sorted", "string_balanced"
    description: str                   # human-readable description of the regime
    is_edge_regime: bool               # True if this regime is at/near constraint boundary


@dataclass
class TestPartition:
    """Structural partition annotation for one test."""
    test_case: TestCaseSpec
    anchors: List[ConstraintAnchor]
    regime: RegimeMapping
    boundary_type: str                 # "min" | "max" | "transition" | "internal" | "degenerate"
    redundancy_score: float            # 0.0 = unique, 1.0 = fully redundant
    partition_power: float             # 0.0 = no coverage value, 1.0 = maximally informative


@dataclass
class PartitionReport:
    """Full partition analysis for one problem."""
    problem_id: str
    test_partitions: List[TestPartition]
    regime_coverage: Dict[str, int]     # regime_id → test count
    uncovered_regimes: List[str]        # regimes with zero tests
    redundancy_clusters: List[List[str]]
    coverage_gaps: List[str]           # structural gap descriptions
    total_partition_power: float       # sum of partition_power across all tests
    avg_partition_power: float


# ═══════════════════════════════════════════════════════════════
# CONSTRAINT REGIME DEFINITIONS (per problem class)
# ═══════════════════════════════════════════════════════════════

def define_regimes(problem_id: str, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Define the input-space partition regimes for a problem.

    Each regime is a distinct region of input space with different
    correctness-relevant properties. This is CLASS-SPECIFIC, not generic.
    """
    regimes = []

    if problem_id in ("two_sum", "three_sum", "four_sum"):
        regimes = [
            {"regime_id": "array_min_length", "description": "Input array at minimum length",
             "is_edge_regime": True, "anchor": ("nums.min_length", "boundary")},
            {"regime_id": "array_interior", "description": "Input array well within length constraints",
             "is_edge_regime": False, "anchor": ("nums.length", "interior")},
            {"regime_id": "target_zero", "description": "Target is zero (sign change boundary)",
             "is_edge_regime": True, "anchor": ("target.zero", "transition")},
            {"regime_id": "target_negative", "description": "Target is negative",
             "is_edge_regime": True, "anchor": ("target.negative", "boundary")},
            {"regime_id": "target_positive", "description": "Target is positive",
             "is_edge_regime": False, "anchor": ("target.positive", "interior")},
            {"regime_id": "values_all_positive", "description": "All array values positive",
             "is_edge_regime": False, "anchor": ("nums.sign", "interior")},
            {"regime_id": "values_all_negative", "description": "All array values negative",
             "is_edge_regime": True, "anchor": ("nums.sign", "boundary")},
            {"regime_id": "values_mixed_sign", "description": "Array has both positive and negative",
             "is_edge_regime": False, "anchor": ("nums.sign_transition", "transition")},
            {"regime_id": "values_duplicate", "description": "Array contains duplicate values",
             "is_edge_regime": False, "anchor": ("nums.uniqueness", "interior")},
            {"regime_id": "values_all_same", "description": "All values identical",
             "is_edge_regime": True, "anchor": ("nums.uniformity", "degenerate")},
            {"regime_id": "values_sorted", "description": "Array is sorted ascending",
             "is_edge_regime": False, "anchor": ("nums.ordering", "interior")},
            {"regime_id": "values_reverse_sorted", "description": "Array is sorted descending",
             "is_edge_regime": False, "anchor": ("nums.ordering", "interior")},
            {"regime_id": "values_unsorted", "description": "Array is unsorted",
             "is_edge_regime": False, "anchor": ("nums.ordering", "interior")},
            {"regime_id": "solution_uses_adjacent", "description": "Solution uses adjacent elements",
             "is_edge_regime": False, "anchor": ("solution.adjacency", "interior")},
            {"regime_id": "solution_uses_non_adjacent", "description": "Solution uses non-adjacent elements",
             "is_edge_regime": False, "anchor": ("solution.non_adjacency", "interior")},
            {"regime_id": "solution_self_element_reuse", "description": "Solution must reuse element (not allowed)",
             "is_edge_regime": True, "anchor": ("constraint.self_reuse", "transition")},
        ]

    elif problem_id == "solve_n_queens":
        regimes = [
            {"regime_id": "n_zero", "description": "n=0 (degenerate base case)",
             "is_edge_regime": True, "anchor": ("n.zero", "degenerate")},
            {"regime_id": "n_one", "description": "n=1 (trivial solution)",
             "is_edge_regime": True, "anchor": ("n.min_nonzero", "boundary")},
            {"regime_id": "n_two_three", "description": "n=2 or n=3 (no solutions exist)",
             "is_edge_regime": True, "anchor": ("n.no_solution", "transition")},
            {"regime_id": "n_four", "description": "n=4 (smallest non-trivial with solutions)",
             "is_edge_regime": True, "anchor": ("n.first_solution", "boundary")},
            {"regime_id": "n_medium", "description": "n=5-7 (moderate complexity)",
             "is_edge_regime": False, "anchor": ("n.medium", "interior")},
            {"regime_id": "n_large", "description": "n=8-9 (approaching constraint max)",
             "is_edge_regime": True, "anchor": ("n.large", "boundary")},
        ]

    elif problem_id in ("max_area", "trap"):
        regimes = [
            {"regime_id": "height_min_length", "description": "Array at minimum length",
             "is_edge_regime": True, "anchor": ("height.min_length", "boundary")},
            {"regime_id": "height_small", "description": "Short array (2-3 elements)",
             "is_edge_regime": True, "anchor": ("height.length", "boundary")},
            {"regime_id": "height_medium", "description": "Medium array (4-6 elements)",
             "is_edge_regime": False, "anchor": ("height.length", "interior")},
            {"regime_id": "height_monotonic_asc", "description": "Heights strictly increasing",
             "is_edge_regime": True, "anchor": ("height.ordering", "transition")},
            {"regime_id": "height_monotonic_desc", "description": "Heights strictly decreasing",
             "is_edge_regime": True, "anchor": ("height.ordering", "transition")},
            {"regime_id": "height_symmetric", "description": "Heights symmetric (palindromic)",
             "is_edge_regime": False, "anchor": ("height.symmetry", "interior")},
            {"regime_id": "height_single_peak", "description": "Single maximum in middle",
             "is_edge_regime": False, "anchor": ("height.topology", "interior")},
            {"regime_id": "height_single_valley", "description": "Single minimum in middle",
             "is_edge_regime": False, "anchor": ("height.topology", "interior")},
            {"regime_id": "height_all_equal", "description": "All heights identical",
             "is_edge_regime": True, "anchor": ("height.uniformity", "degenerate")},
            {"regime_id": "height_zero_values", "description": "Contains zero heights",
             "is_edge_regime": True, "anchor": ("height.zero", "boundary")},
            {"regime_id": "height_extreme_contrast", "description": "Very high and very low values adjacent",
             "is_edge_regime": False, "anchor": ("height.contrast", "interior")},
        ]

    elif problem_id == "valid_parentheses":
        regimes = [
            {"regime_id": "string_empty", "description": "Empty string (degenerate base case)",
             "is_edge_regime": True, "anchor": ("s.empty", "degenerate")},
            {"regime_id": "string_length_one", "description": "Single character (impossible to balance)",
             "is_edge_regime": True, "anchor": ("s.min_length", "boundary")},
            {"regime_id": "string_length_two", "description": "Two characters (minimal valid/invalid)",
             "is_edge_regime": True, "anchor": ("s.min_pair", "boundary")},
            {"regime_id": "balanced_simple", "description": "Simple balanced: ()",
             "is_edge_regime": False, "anchor": ("s.balanced", "interior")},
            {"regime_id": "balanced_nested", "description": "Nested balanced: {[]}",
             "is_edge_regime": False, "anchor": ("s.balanced_nested", "interior")},
            {"regime_id": "balanced_sequential", "description": "Sequential balanced: ()[]{}",
             "is_edge_regime": False, "anchor": ("s.balanced_sequential", "interior")},
            {"regime_id": "unbalanced_wrong_type", "description": "Mismatched types: (]",
             "is_edge_regime": True, "anchor": ("s.type_mismatch", "transition")},
            {"regime_id": "unbalanced_wrong_order", "description": "Wrong nesting order: ([)]",
             "is_edge_regime": True, "anchor": ("s.order_mismatch", "transition")},
            {"regime_id": "unbalanced_unclosed", "description": "Missing closing: (",
             "is_edge_regime": True, "anchor": ("s.missing_close", "boundary")},
            {"regime_id": "unbalanced_unopened", "description": "Missing opening: )",
             "is_edge_regime": True, "anchor": ("s.missing_open", "boundary")},
            {"regime_id": "unbalanced_extra_close", "description": "Extra closing: ())",
             "is_edge_regime": True, "anchor": ("s.extra_close", "boundary")},
            {"regime_id": "unbalanced_extra_open", "description": "Extra opening: (()",
             "is_edge_regime": True, "anchor": ("s.extra_open", "boundary")},
            {"regime_id": "all_one_type", "description": "All same bracket type: ((( )))",
             "is_edge_regime": False, "anchor": ("s.uniform_type", "interior")},
            {"regime_id": "all_three_types", "description": "All three bracket types used",
             "is_edge_regime": False, "anchor": ("s.type_diversity", "interior")},
        ]

    else:
        # Generic fallback — basic regime classification
        regimes = [
            {"regime_id": "input_min_size", "description": "Input at minimum size",
             "is_edge_regime": True, "anchor": ("input.min_size", "boundary")},
            {"regime_id": "input_max_size", "description": "Input at maximum size",
             "is_edge_regime": True, "anchor": ("input.max_size", "boundary")},
            {"regime_id": "input_interior", "description": "Input in middle of constraint range",
             "is_edge_regime": False, "anchor": ("input.size", "interior")},
            {"regime_id": "values_boundary", "description": "Values at constraint boundaries",
             "is_edge_regime": True, "anchor": ("input.value_boundary", "boundary")},
            {"regime_id": "values_interior", "description": "Values well within constraints",
             "is_edge_regime": False, "anchor": ("input.value_interior", "interior")},
        ]

    return regimes


# ═══════════════════════════════════════════════════════════════
# TEST → REGIME CLASSIFIER
# ═══════════════════════════════════════════════════════════════

def classify_test_regimes(
    test_case: TestCaseSpec,
    constraints: Dict[str, Any],
    problem_id: str,
) -> Tuple[List[ConstraintAnchor], RegimeMapping, str]:
    """Classify a test case into its constraint regimes.

    Returns:
        (anchors, regime, boundary_type)
    """
    regimes = define_regimes(problem_id, constraints)
    anchors = []
    matched_regimes = []
    boundary_type = "internal"

    for val_idx, val in enumerate(test_case.input):
        if isinstance(val, list) and len(val) > 0:
            # Array-based problems
            arr_len = len(val)
            min_len = None
            for cname, cval in constraints.items():
                if isinstance(cval, dict) and "min_length" in cval:
                    min_len = cval["min_length"]

            # Size-based anchors
            if min_len is not None and arr_len == min_len:
                anchors.append(ConstraintAnchor(
                    name=f"input_{val_idx}.min_length",
                    category="boundary",
                    constraint_path=f"input[{val_idx}].min_length",
                ))
                boundary_type = "min"
            elif min_len is not None and arr_len <= min_len + 2:
                anchors.append(ConstraintAnchor(
                    name=f"input_{val_idx}.near_min_length",
                    category="boundary",
                    constraint_path=f"input[{val_idx}].length",
                ))
                boundary_type = "min"

            # Value-based anchors
            int_vals = [v for v in val if isinstance(v, int) and not isinstance(v, bool)]
            if int_vals:
                has_negative = any(v < 0 for v in int_vals)
                has_positive = any(v > 0 for v in int_vals)
                has_zero = any(v == 0 for v in int_vals)
                all_same = len(set(int_vals)) == 1

                if has_negative and has_positive:
                    anchors.append(ConstraintAnchor(
                        name=f"input_{val_idx}.mixed_sign",
                        category="transition",
                        constraint_path=f"input[{val_idx}].sign",
                    ))
                elif has_negative and not has_positive:
                    anchors.append(ConstraintAnchor(
                        name=f"input_{val_idx}.all_negative",
                        category="boundary",
                        constraint_path=f"input[{val_idx}].sign",
                    ))
                elif has_zero:
                    anchors.append(ConstraintAnchor(
                        name=f"input_{val_idx}.contains_zero",
                        category="boundary",
                        constraint_path=f"input[{val_idx}].value",
                    ))
                    boundary_type = "transition"

                if all_same and arr_len > 1:
                    anchors.append(ConstraintAnchor(
                        name=f"input_{val_idx}.all_same",
                        category="degenerate",
                        constraint_path=f"input[{val_idx}].uniformity",
                    ))
                    boundary_type = "degenerate"

                # Ordering check
                if int_vals == sorted(int_vals) and len(int_vals) > 2:
                    anchors.append(ConstraintAnchor(
                        name=f"input_{val_idx}.sorted_asc",
                        category="interior",
                        constraint_path=f"input[{val_idx}].ordering",
                    ))
                elif int_vals == sorted(int_vals, reverse=True) and len(int_vals) > 2:
                    anchors.append(ConstraintAnchor(
                        name=f"input_{val_idx}.sorted_desc",
                        category="interior",
                        constraint_path=f"input[{val_idx}].ordering",
                    ))

                # Duplicate check
                if len(int_vals) != len(set(int_vals)):
                    anchors.append(ConstraintAnchor(
                        name=f"input_{val_idx}.has_duplicates",
                        category="interior",
                        constraint_path=f"input[{val_idx}].uniqueness",
                    ))

        elif isinstance(val, str):
            # String-based problems
            str_len = len(val)
            min_len = None
            max_len = None
            for cname, cval in constraints.items():
                if isinstance(cval, dict):
                    if "min_length" in cval:
                        min_len = cval["min_length"]
                    if "max_length" in cval:
                        max_len = cval["max_length"]

            if str_len == 0:
                anchors.append(ConstraintAnchor(
                    name=f"input_{val_idx}.empty",
                    category="degenerate",
                    constraint_path=f"input[{val_idx}].length",
                ))
                boundary_type = "degenerate"
            elif str_len == 1:
                anchors.append(ConstraintAnchor(
                    name=f"input_{val_idx}.single_char",
                    category="boundary",
                    constraint_path=f"input[{val_idx}].length",
                ))
                boundary_type = "min"
            elif min_len is not None and str_len == min_len:
                anchors.append(ConstraintAnchor(
                    name=f"input_{val_idx}.min_length",
                    category="boundary",
                    constraint_path=f"input[{val_idx}].length",
                ))
                boundary_type = "min"

            # Parentheses-specific
            if problem_id == "valid_parentheses":
                if str_len > 0:
                    opens = val.count('(') + val.count('[') + val.count('{')
                    closes = val.count(')') + val.count(']') + val.count('}')
                    bracket_types = set(c for c in val if c in '()[]{}')

                    if opens == closes and str_len > 0:
                        # Could be balanced — check structural
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
                            if len(bracket_types) >= 6:
                                anchors.append(ConstraintAnchor(
                                    name=f"input_{val_idx}.balanced_all_types",
                                    category="interior",
                                    constraint_path=f"input[{val_idx}].balance",
                                ))
                            elif len(bracket_types) >= 2:
                                anchors.append(ConstraintAnchor(
                                    name=f"input_{val_idx}.balanced_multi_type",
                                    category="interior",
                                    constraint_path=f"input[{val_idx}].balance",
                                ))
                            else:
                                anchors.append(ConstraintAnchor(
                                    name=f"input_{val_idx}.balanced_single_type",
                                    category="interior",
                                    constraint_path=f"input[{val_idx}].balance",
                                ))
                        else:
                            if '(' in val and ']' in val or '[' in val and ')' in val:
                                anchors.append(ConstraintAnchor(
                                    name=f"input_{val_idx}.type_mismatch",
                                    category="transition",
                                    constraint_path=f"input[{val_idx}].mismatch",
                                ))
                                boundary_type = "transition"
                            elif not balanced and str_len <= 4:
                                anchors.append(ConstraintAnchor(
                                    name=f"input_{val_idx}.short_unbalanced",
                                    category="boundary",
                                    constraint_path=f"input[{val_idx}].balance",
                                ))
                                boundary_type = "transition"

        elif isinstance(val, int) and not isinstance(val, bool):
            # Scalar integer problems (N-Queens, etc.)
            if val == 0:
                anchors.append(ConstraintAnchor(
                    name=f"input_{val_idx}.zero",
                    category="degenerate",
                    constraint_path=f"input[{val_idx}].value",
                ))
                boundary_type = "degenerate"
            elif val == 1:
                anchors.append(ConstraintAnchor(
                    name=f"input_{val_idx}.one",
                    category="boundary",
                    constraint_path=f"input[{val_idx}].value",
                ))
                boundary_type = "min"

            for cname, cval in constraints.items():
                if isinstance(cval, dict):
                    if "min" in cval and val == cval["min"]:
                        anchors.append(ConstraintAnchor(
                            name=f"input_{val_idx}.{cname}_min",
                            category="boundary",
                            constraint_path=f"input[{val_idx}].{cname}",
                        ))
                        boundary_type = "min"
                    if "max" in cval and val == cval["max"]:
                        anchors.append(ConstraintAnchor(
                            name=f"input_{val_idx}.{cname}_max",
                            category="boundary",
                            constraint_path=f"input[{val_idx}].{cname}",
                        ))
                        boundary_type = "max"

    # Match anchors to regime definitions using keyword-based matching
    anchor_keywords = set()
    for a in anchors:
        # Extract meaningful keywords from anchor name
        # e.g., "input_0.all_negative" → {"all_negative", "negative", "all"}
        parts = a.name.split(".")
        if len(parts) > 1:
            anchor_keywords.add(parts[1])  # "all_negative"
            for p in parts[1].split("_"):
                if len(p) > 2:
                    anchor_keywords.add(p)

    best_regime = None
    best_match_score = 0

    for reg_def in regimes:
        reg_id = reg_def["regime_id"]
        anchor_tuple = reg_def.get("anchor", (None, None))
        anchor_name = anchor_tuple[0] if isinstance(anchor_tuple, tuple) else None

        # Extract keywords from regime
        regime_keywords = set()
        for part in reg_id.split("_"):
            if len(part) > 2:
                regime_keywords.add(part)
        if anchor_name:
            for part in anchor_name.split("."):
                for sub in part.split("_"):
                    if len(sub) > 2:
                        regime_keywords.add(sub)

        # Count overlapping keywords
        overlap = len(anchor_keywords & regime_keywords)
        if overlap > best_match_score:
            best_match_score = overlap
            best_regime = reg_def

    # Fallback: if no match found, pick first regime
    if best_regime is None:
        best_regime = regimes[0] if regimes else {
            "regime_id": "input_interior",
            "description": "Input in middle of constraint range",
            "is_edge_regime": False,
            "anchor": ("input.size", "interior"),
        }

    regime = RegimeMapping(
        regime_id=best_regime["regime_id"],
        description=best_regime["description"],
        is_edge_regime=best_regime.get("is_edge_regime", False),
    )

    # Determine boundary type from anchors
    if not anchors:
        boundary_type = "internal"

    return anchors, regime, boundary_type


# ═══════════════════════════════════════════════════════════════
# REDUNDANCY COMPUTATION (input-space based)
# ═══════════════════════════════════════════════════════════════

def compute_redundancy(
    test_case: TestCaseSpec,
    all_partitions: List[TestPartition],
) -> float:
    """Compute how redundant this test is with respect to existing partitions.

    0.0 = completely unique (covers regimes no other test covers)
    1.0 = fully redundant (same regimes as another test)
    """
    if not all_partitions:
        return 0.0

    # Get this test's regime IDs
    test_regimes = set()
    # We need to compute the regimes for this test first
    return 0.0  # placeholder — computed in main loop


def compute_partition_power(
    test_case: TestCaseSpec,
    anchors: List[ConstraintAnchor],
    regime: RegimeMapping,
    boundary_type: str,
    redundancy: float,
    regime_test_counts: Dict[str, int],
) -> float:
    """Compute how much structural coverage value this test adds.

    High partition power = test covers under-tested regimes.
    Low partition power = test covers already well-covered regimes.

    Formula:
      power = (regime_weight × boundary_bonus × uniqueness) / (1 + redundancy)

    regime_weight: edge regimes are weighted higher (rarer, more informative)
    boundary_bonus: boundary tests are more valuable than interior tests
    uniqueness: 1 / regime_test_counts[regime_id] (diminishing returns)
    redundancy: penalizes overlap with other tests
    """
    # Regime weight: edge regimes are 2x as valuable as interior
    regime_weight = 2.0 if regime.is_edge_regime else 1.0

    # Boundary bonus: boundary/degenerate tests are more informative
    boundary_bonus = {
        "boundary": 1.5,
        "transition": 1.3,
        "degenerate": 1.8,
        "internal": 1.0,
    }.get(boundary_type, 1.0)

    # Uniqueness: diminishing returns for multiple tests in same regime
    regime_count = regime_test_counts.get(regime.regime_id, 1)
    uniqueness = 1.0 / regime_count

    # Redundancy penalty
    redundancy_penalty = 1.0 / (1.0 + redundancy * 2.0)

    power = regime_weight * boundary_bonus * uniqueness * redundancy_penalty
    return round(power, 3)


# ═══════════════════════════════════════════════════════════════
# MAIN AUDIT FUNCTION
# ═══════════════════════════════════════════════════════════════

def audit_partition_coverage(
    problem_id: str,
    test_cases: List[TestCaseSpec],
    constraints: Dict[str, Any],
) -> PartitionReport:
    """Generate structural partition audit for one problem.

    This is the v2 replacement for sensitivity analysis.
    Does NOT use:
      - Reference function ΔE
      - Output variation under mutation
      - Solution simulation

    Uses ONLY:
      - Input-space classification
      - Constraint regime definitions
      - Structural redundancy detection
    """
    all_partitions: List[TestPartition] = []

    # First pass: classify all tests into regimes
    regime_counts: Dict[str, int] = {}
    regime_anchors: Dict[str, List[TestCaseSpec]] = {}

    for tc in test_cases:
        anchors, regime, boundary_type = classify_test_regimes(tc, constraints, problem_id)
        regime_counts[regime.regime_id] = regime_counts.get(regime.regime_id, 0) + 1
        if regime.regime_id not in regime_anchors:
            regime_anchors[regime.regime_id] = []
        regime_anchors[regime.regime_id].append(tc)

    # Second pass: compute redundancy and partition power
    for tc in test_cases:
        anchors, regime, boundary_type = classify_test_regimes(tc, constraints, problem_id)

        # Redundancy: how many other tests are in the same regime?
        regime_count = regime_counts.get(regime.regime_id, 1)
        redundancy = (regime_count - 1) / regime_count if regime_count > 1 else 0.0

        # Partition power
        power = compute_partition_power(
            tc, anchors, regime, boundary_type, redundancy, regime_counts,
        )

        partition = TestPartition(
            test_case=tc,
            anchors=anchors,
            regime=regime,
            boundary_type=boundary_type,
            redundancy_score=round(redundancy, 3),
            partition_power=power,
        )
        all_partitions.append(partition)

    # Define all possible regimes and find uncovered ones
    all_regimes = define_regimes(problem_id, constraints)
    all_regime_ids = [r["regime_id"] for r in all_regimes]
    covered_regime_ids = set(tp.regime.regime_id for tp in all_partitions)
    uncovered = [rid for rid in all_regime_ids if rid not in covered_regime_ids]

    # Redundancy clusters: group tests by regime
    clusters = []
    for reg_id, tests in regime_anchors.items():
        if len(tests) > 1:
            clusters.append([tc.label for tc in tests])

    # Coverage gaps
    gaps = []
    for reg_id in uncovered:
        reg_def = next(r for r in all_regimes if r["regime_id"] == reg_id)
        gaps.append(f"Uncovered regime: {reg_def['description']} ({reg_id})")

    # Add gaps for boundary-weak problems
    has_boundary = any(tp.boundary_type in ("min", "max") for tp in all_partitions)
    if not has_boundary:
        gaps.append("No tests at constraint min/max boundaries")

    has_degenerate = any(tp.boundary_type == "degenerate" for tp in all_partitions)
    if not has_degenerate:
        gaps.append("No tests at degenerate cases (empty, zero, n=0)")

    # Totals
    total_power = sum(tp.partition_power for tp in all_partitions)
    avg_power = total_power / len(all_partitions) if all_partitions else 0.0

    return PartitionReport(
        problem_id=problem_id,
        test_partitions=all_partitions,
        regime_coverage=dict(regime_counts),
        uncovered_regimes=uncovered,
        redundancy_clusters=clusters,
        coverage_gaps=gaps,
        total_partition_power=round(total_power, 3),
        avg_partition_power=round(avg_power, 3),
    )


# ═══════════════════════════════════════════════════════════════
# REPORT FORMATTING
# ═══════════════════════════════════════════════════════════════

def format_partition_report(report: PartitionReport) -> str:
    """Human-readable partition audit report."""
    lines = []
    lines.append(f"=" * 65)
    lines.append(f"STRUCTURAL PARTITION AUDIT: {report.problem_id}")
    lines.append(f"=" * 65)
    lines.append(f"Tests analyzed: {len(report.test_partitions)}")
    lines.append(f"Regimes covered: {len(report.regime_coverage)}")
    lines.append(f"Regimes uncovered: {len(report.uncovered_regimes)}")
    lines.append(f"Total partition power: {report.total_partition_power:.3f}")
    lines.append(f"Avg partition power: {report.avg_partition_power:.3f}")
    lines.append(f"Redundancy clusters: {len(report.redundancy_clusters)}")
    lines.append("")

    # Regime coverage table
    lines.append("REGIME COVERAGE:")
    all_regimes = define_regimes(report.problem_id, {})
    for reg_def in all_regimes:
        reg_id = reg_def["regime_id"]
        count = report.regime_coverage.get(reg_id, 0)
        status = f"✓ {count}" if count > 0 else "✗ 0"
        edge = " [EDGE]" if reg_def.get("is_edge_regime") else ""
        lines.append(f"  {status}  {reg_id}{edge}: {reg_def['description']}")
    lines.append("")

    # Per-test partition annotation
    lines.append("PER-TEST PARTITION:")
    for tp in sorted(report.test_partitions, key=lambda p: p.partition_power, reverse=True):
        labels = [a.name for a in tp.anchors]
        flag = ""
        if tp.redundancy_score > 0.5:
            flag = " ⚠ REDUNDANT"
        elif tp.partition_power < 0.3:
            flag = " ⚠ LOW POWER"
        lines.append(f"  {tp.test_case.label}:")
        lines.append(f"    regime: {tp.regime.regime_id} (edge={tp.regime.is_edge_regime})")
        lines.append(f"    boundary: {tp.boundary_type}")
        lines.append(f"    anchors: {', '.join(labels) if labels else 'none'}")
        lines.append(f"    redundancy: {tp.redundancy_score:.3f}, power: {tp.partition_power:.3f}{flag}")
    lines.append("")

    if report.uncovered_regimes:
        lines.append(f"UNCOVERED REGIMES ({len(report.uncovered_regimes)}):")
        for reg_id in report.uncovered_regimes:
            reg_def = next(r for r in all_regimes if r["regime_id"] == reg_id)
            lines.append(f"  ✗ {reg_id}: {reg_def['description']}")
        lines.append("")

    if report.coverage_gaps:
        lines.append(f"COVERAGE GAPS ({len(report.coverage_gaps)}):")
        for gap in report.coverage_gaps:
            lines.append(f"  - {gap}")
        lines.append("")

    if report.redundancy_clusters:
        lines.append(f"REDUNDANCY CLUSTERS ({len(report.redundancy_clusters)}):")
        for cluster in report.redundancy_clusters:
            lines.append(f"  {cluster}")
        lines.append("")

    return "\n".join(lines)
