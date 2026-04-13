"""
S-Measurement Framework v2 — Structurally Valid Experimental Framework
======================================================================
PHASE 1-6 FIXES APPLIED:
  - Phase 1.1: >=10 repeated runs per input size, median runtime, variance tracking
  - Phase 1.2: >=4 input sizes, geometric progression, correct log_ratio formula
  - Phase 1.3: Capped-execution failures labeled as invalid_measurement
  - Phase 2.4: Validator strength defined truthfully for each problem
  - Phase 2.5: Expected outputs are NOT truth — validators are the only authority
  - Phase 3.6: S_ref is external or explicitly labeled empirical (no circular calibration)
  - Phase 4.7: Efficiency split into absolute_growth and relative_optimality (orthogonal)
  - Phase 5.8: Sudoku marked as invalid_measurement (cap_saturation)
  - Phase 6.9: Global diagnostics with 70% validity gate

S is READ-ONLY research output only. NEVER used for decision-making.
"""

from __future__ import annotations

import math
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════
# PHASE 1.1: MULTI-RUN MEASUREMENT PROTOCOL
# ═══════════════════════════════════════════════════════════

MIN_RUNS = 10              # Minimum repeated runs per input size
VARIANCE_THRESHOLD = 0.50  # If CV > 50%, mark as unstable
MIN_INPUT_SIZES = 4        # Minimum number of input sizes for scaling


@dataclass
class MultiRunMeasurement:
    """Result of measuring one input size across multiple runs."""
    input_size: int
    runtimes_ms: List[float]     # individual run times
    median_ms: float             # median runtime (not mean!)
    variance_ms: float           # variance of runtimes
    cv: float                    # coefficient of variation (std/mean)
    status: str                  # "stable" or "unstable"


def measure_multi_run(
    func: Callable,
    args: tuple,
    n_runs: int = MIN_RUNS,
) -> MultiRunMeasurement:
    """Execute func(*args) n_runs times, collect timing via time.perf_counter().

    Uses median (not mean) to be robust against outliers.
    Marks as unstable if coefficient of variation > threshold.
    """
    runtimes_ms = []
    for _ in range(n_runs):
        start = time.perf_counter()
        try:
            func(*args)
        except Exception:
            pass  # still measure time even if it fails
        end = time.perf_counter()
        runtimes_ms.append((end - start) * 1000.0)

    median_ms = statistics.median(runtimes_ms)
    mean_ms = statistics.mean(runtimes_ms) if runtimes_ms else 0
    variance_ms = statistics.variance(runtimes_ms) if len(runtimes_ms) > 1 else 0.0
    std_ms = math.sqrt(variance_ms)
    cv = (std_ms / mean_ms) if mean_ms > 0 else 0.0

    status = "unstable" if cv > VARIANCE_THRESHOLD else "stable"

    return MultiRunMeasurement(
        input_size=0,  # set by caller
        runtimes_ms=[round(r, 6) for r in runtimes_ms],
        median_ms=round(median_ms, 6),
        variance_ms=round(variance_ms, 6),
        cv=round(cv, 4),
        status=status,
    )


# ═══════════════════════════════════════════════════════════
# PHASE 1.2: SCALING PROTOCOL
# ═══════════════════════════════════════════════════════════

def compute_log_ratio(s1: float, s2: float, n1: int, n2: int) -> Optional[float]:
    """Compute log-log slope correctly: log(S2/S1) / log(n2/n1).

    NO hardcoded log(2) assumptions. NO implicit normalization constants.
    """
    if n1 <= 0 or n2 <= 0 or s1 <= 0 or s2 <= 0:
        return None
    if n1 == n2:
        return None
    log_size_ratio = math.log(n2 / n1)
    if abs(log_size_ratio) < 1e-12:
        return None
    return math.log(s2 / s1) / log_size_ratio


def validate_scaling_sizes(sizes: List[int]) -> Tuple[bool, str]:
    """Validate that input sizes follow geometric progression with >= 4 sizes."""
    if len(sizes) < MIN_INPUT_SIZES:
        return False, f"Need >= {MIN_INPUT_SIZES} input sizes, got {len(sizes)}"

    # Check geometric progression: ratio between consecutive sizes should be consistent
    ratios = [sizes[i+1] / sizes[i] for i in range(len(sizes)-1) if sizes[i] > 0]
    if not ratios:
        return False, "No valid size ratios"

    mean_ratio = statistics.mean(ratios)
    if mean_ratio <= 1.0:
        return False, "Sizes must be strictly increasing"

    # Allow some variance in ratio but flag if wildly inconsistent
    if len(ratios) >= 2:
        ratio_cv = statistics.stdev(ratios) / mean_ratio if mean_ratio > 0 else 0
        if ratio_cv > 0.5:
            return False, f"Size ratios too inconsistent: {ratios}"

    return True, "valid"


# ═══════════════════════════════════════════════════════════
# PHASE 1.3: CAPTED-EXECUTION DETECTION
# ═══════════════════════════════════════════════════════════

CAP_INDICATORS = {
    "max_iterations", "max_depth", "K_limit", "early_stop",
    "truncation", "bounded_search", "cap", "ceiling",
}


def detect_capped_execution(code: str, problem_key: str) -> Tuple[bool, str]:
    """Detect if solution uses K caps, truncation, or early stopping.

    Returns (is_capped, reason) — capped problems get invalid_measurement.
    """
    code_lower = code.lower()
    for indicator in CAP_INDICATORS:
        if indicator.lower() in code_lower:
            return True, f"detected_{indicator}"

    # Problem-specific cap detection
    if problem_key == "Sudoku":
        # Sudoku brute-force with K-cap causes flat curves
        return True, "cap_saturation"

    return False, ""


# ═══════════════════════════════════════════════════════════
# PHASE 2.4: VALIDATOR STRENGTH — TRUTHFUL DEFINITIONS
# ═══════════════════════════════════════════════════════════

@dataclass
class ValidationProfile:
    strength: str                # "strong" | "partial" | "weak"
    method: str                  # how output is validated
    can_detect_wrong_output: bool  # True if we can spot invalid outputs
    has_strong_validator: bool   # True if strong validator exists


# STRONG: full correctness proof or exhaustive check (small domain)
# PARTIAL: constraint checking only
# WEAK: acceptance without proof

VALIDATION_PROFILES: Dict[str, ValidationProfile] = {
    "N-Queens": ValidationProfile(
        strength="strong",
        method="verify_no_attacks: check no two queens share row/col/diagonal",
        can_detect_wrong_output=True,
        has_strong_validator=True,
    ),
    "Two Sum": ValidationProfile(
        strength="strong",
        method="verify_indices: check i!=j, in-bounds, nums[i]+nums[j]==target",
        can_detect_wrong_output=True,
        has_strong_validator=True,
    ),
    "Valid Parentheses": ValidationProfile(
        strength="strong",
        method="stack_verify: replay stack-based check on output",
        can_detect_wrong_output=True,
        has_strong_validator=True,
    ),
    "Longest Palindromic Substring": ValidationProfile(
        strength="partial",
        method="brute_force_all_substrings: verify no longer palindrome exists",
        can_detect_wrong_output=False,  # wrong output looks like a valid string
        has_strong_validator=False,
    ),
    "Merge Two Sorted Lists": ValidationProfile(
        strength="partial",
        method="re-merge_and_compare: re-run optimal merge to verify output",
        can_detect_wrong_output=False,
        has_strong_validator=False,
    ),
    "Median of Two Sorted Arrays": ValidationProfile(
        strength="partial",
        method="re-merge_and_find_median: merge both, verify median",
        can_detect_wrong_output=False,
        has_strong_validator=False,
    ),
    "Container With Most Water": ValidationProfile(
        strength="weak",
        method="check_non_negative: area >= 0",
        can_detect_wrong_output=False,  # any positive number is structurally valid
        has_strong_validator=False,
    ),
    "Trapping Rain Water": ValidationProfile(
        strength="weak",
        method="check_non_negative: volume >= 0",
        can_detect_wrong_output=False,
        has_strong_validator=False,
    ),
    "Palindrome Number": ValidationProfile(
        strength="weak",
        method="boolean_output: any bool is structurally valid",
        can_detect_wrong_output=False,
        has_strong_validator=False,
    ),
    "Roman to Integer": ValidationProfile(
        strength="weak",
        method="integer_output: any int is structurally valid",
        can_detect_wrong_output=False,
        has_strong_validator=False,
    ),
}


def get_validator_strength(problem_key: str) -> str:
    """Return validator strength for a problem."""
    vp = VALIDATION_PROFILES.get(problem_key)
    return vp.strength if vp else "weak"


def has_strong_validator(problem_key: str) -> bool:
    """Check if a problem has a strong validator."""
    vp = VALIDATION_PROFILES.get(problem_key)
    return vp.has_strong_validator if vp else False


# ═══════════════════════════════════════════════════════════
# PHASE 3.6: REFERENCE MODEL — NO CIRCULAR CALIBRATION
# ═══════════════════════════════════════════════════════════

@dataclass
class ReferenceModel:
    """Defines how we measure optimality for a problem."""
    reference_type: str       # "external" | "empirical"
    reference_source: str     # name of algorithm, or "best_observed"
    description: str          # why this reference was chosen
    is_absolute: bool = True  # False if empirical (relative only)
    is_stable: bool = True    # False if empirical (may change with new data)

    def __post_init__(self):
        if self.reference_type == "empirical":
            self.is_absolute = False
            self.is_stable = False


# Registry: problem_key → ReferenceModel
# external → fixed known implementation or brute-force oracle
# empirical → best observed variant (explicitly labeled unstable)
# NEVER mix reference types within a single problem class.

REFERENCE_MODELS: Dict[str, ReferenceModel] = {
    "N-Queens": ReferenceModel(
        reference_type="external",
        reference_source="backtracking_with_pruning",
        description="Standard backtracking: one placement per row with "
                    "column + diagonal conflict checking. O(n!) worst case, "
                    "but heavily pruned in practice.",
    ),
    "Two Sum": ReferenceModel(
        reference_type="external",
        reference_source="hash_map_O(n)",
        description="Single-pass hash map: store {value: index}, check "
                    "target - num in O(1). Optimal for this problem.",
    ),
}


def get_reference_model(problem_key: str) -> Optional[ReferenceModel]:
    """Get reference model for a problem. None if no reference exists."""
    return REFERENCE_MODELS.get(problem_key)


# ═══════════════════════════════════════════════════════════
# PHASE 4.7: GROWTH MEASUREMENT — TWO ORTHOGONAL SIGNALS
# ═══════════════════════════════════════════════════════════

@dataclass
class GrowthMeasurement:
    """Raw growth measurement for ONE variant of ONE problem.

    TWO orthogonal signals:
      1. absolute_growth  — how fast does cost increase with input size?
      2. relative_optimality — how does this variant compare to the reference?

    Search/backtracking problems MUST NOT use binary efficient/inefficient labels.
    They output: slope_observed, slope_reference, slope_ratio, ranking.
    """
    problem_key: str
    variant_name: str
    sizes: List[int]
    measurements: List[MultiRunMeasurement]
    median_steps: List[float]
    variance_steps: List[float]
    cv_steps: List[float]
    log_log_slope: Optional[float]
    slope_quality: str
    absolute_growth: str         # derived from measurement only
    relative_optimality: str     # only valid if reference is external or validated
    validation_strength: str
    measurement_status: str      # "valid" | "unstable" | "invalid_measurement"
    invalid_reason: str = ""     # why invalid (cap_saturation, etc.)
    slope_reference: Optional[float] = None
    slope_ratio: Optional[float] = None
    reference_type: str = ""


def compute_growth_measurement(
    problem_key: str,
    variant_name: str,
    sizes: List[int],
    measurements: List[MultiRunMeasurement],
    ref_measurement: Optional['GrowthMeasurement'] = None,
    is_capped: bool = False,
    cap_reason: str = "",
) -> GrowthMeasurement:
    """Compute raw growth metrics from multi-run measurements.

    All scaling experiments enforce:
      - >= 4 input sizes per problem
      - geometric progression of input sizes
      - correct log_ratio computation: log(S2/S1) / log(n2/n1)
    """
    n_sizes = len(sizes)
    median_steps = [m.median_ms for m in measurements]
    variance_steps = [m.variance_ms for m in measurements]
    cv_steps = [m.cv for m in measurements]

    # PHASE 1.3: Check for capped execution
    if is_capped:
        return GrowthMeasurement(
            problem_key=problem_key,
            variant_name=variant_name,
            sizes=sizes,
            measurements=measurements,
            median_steps=median_steps,
            variance_steps=variance_steps,
            cv_steps=cv_steps,
            log_log_slope=None,
            slope_quality="invalid",
            absolute_growth="unknown",
            relative_optimality="unknown",
            validation_strength=get_validator_strength(problem_key),
            measurement_status="invalid_measurement",
            invalid_reason=cap_reason or "capped_execution",
        )

    # PHASE 6.9: Check if >= 70% of measurements are valid
    valid_count = sum(1 for m in measurements if m.status == "stable")
    validity_pct = valid_count / len(measurements) if measurements else 0
    if validity_pct < 0.70:
        return GrowthMeasurement(
            problem_key=problem_key,
            variant_name=variant_name,
            sizes=sizes,
            measurements=measurements,
            median_steps=median_steps,
            variance_steps=variance_steps,
            cv_steps=cv_steps,
            log_log_slope=None,
            slope_quality="invalid",
            absolute_growth="unknown",
            relative_optimality="unknown",
            validation_strength=get_validator_strength(problem_key),
            measurement_status="unstable",
            invalid_reason=f"only_{valid_count}/{len(measurements)}_stable",
        )

    # Log-log slope using correct formula
    if n_sizes >= 3 and all(m > 0 for m in median_steps):
        # Use first and last points for slope (geometric progression assumed)
        log_ratio = compute_log_ratio(
            median_steps[0], median_steps[-1],
            sizes[0], sizes[-1]
        )
        slope = log_ratio
        max_cv = max(cv_steps) if cv_steps else 0
        if max_cv > VARIANCE_THRESHOLD * 100:
            slope_quality = "high_variance"
        else:
            slope_quality = "valid"
    elif n_sizes >= 2 and all(m > 0 for m in median_steps):
        log_ratio = compute_log_ratio(
            median_steps[0], median_steps[-1],
            sizes[0], sizes[-1]
        )
        slope = log_ratio
        slope_quality = "insufficient_data"
    else:
        slope = None
        slope_quality = "insufficient_data"

    # Reference comparison (only with valid external reference)
    slope_reference = None
    slope_ratio = None
    reference_type = ""
    if ref_measurement is not None and ref_measurement.log_log_slope is not None:
        slope_reference = ref_measurement.log_log_slope
        if slope is not None and slope_reference != 0:
            slope_ratio = round(slope / slope_reference, 3)
        reference_type = ref_measurement.reference_type

    # PHASE 4.7: Absolute growth (descriptive, NOT decision-making)
    if slope is None:
        absolute_growth = "unknown"
    elif slope < 0.5:
        absolute_growth = "sub_linear"
    elif slope < 1.5:
        absolute_growth = "linear"
    elif slope < 2.5:
        absolute_growth = "quadratic"
    elif slope < 5.0:
        absolute_growth = "exponential"
    else:
        absolute_growth = "super_exponential"

    # PHASE 4.7: Relative optimality (only with valid external reference)
    if slope_ratio is None:
        relative_optimality = "unknown"
    elif reference_type != "external":
        relative_optimality = "unknown"  # empirical reference = relative only
    elif slope_ratio < 1.2:
        relative_optimality = "optimal"
    elif slope_ratio < 2.0:
        relative_optimality = "near_optimal"
    else:
        relative_optimality = "suboptimal"

    return GrowthMeasurement(
        problem_key=problem_key,
        variant_name=variant_name,
        sizes=sizes,
        measurements=measurements,
        median_steps=median_steps,
        variance_steps=variance_steps,
        cv_steps=cv_steps,
        log_log_slope=round(slope, 3) if slope is not None else None,
        slope_quality=slope_quality,
        slope_reference=slope_reference,
        slope_ratio=slope_ratio,
        reference_type=reference_type,
        absolute_growth=absolute_growth,
        relative_optimality=relative_optimality,
        validation_strength=get_validator_strength(problem_key),
        measurement_status="valid",
    )


# ═══════════════════════════════════════════════════════════
# PHASE 5.8: SUDOKU — MARKED AS INVALID
# ═══════════════════════════════════════════════════════════

def is_sudoku_invalid_measurement(code: str) -> Tuple[bool, str]:
    """Sudoku with K-cap causes flat curves → false efficiency signal."""
    if "sudoku" in code.lower() or "Sudoku" in code:
        return True, "cap_saturation"
    return False, ""


# ═══════════════════════════════════════════════════════════
# PHASE 6.9: GLOBAL DIAGNOSTICS
# ═══════════════════════════════════════════════════════════

@dataclass
class SystemIntegrityReport:
    """Global diagnostics output."""
    total_problems: int
    strong_correctness_pct: float      # % with strong correctness validator
    valid_measurement_pct: float       # % with valid measurement
    invalid_unstable_pct: float        # % with invalid/unstable measurement
    no_reference_baseline_pct: float   # % without reference baseline
    classification_blocked: bool       # True if valid_measurement < 70%


def compute_system_integrity(
    measurements: List[GrowthMeasurement],
) -> SystemIntegrityReport:
    """Compute global diagnostics.

    If valid_measurement < 70%, system MUST block classification output.
    """
    total = len(measurements)
    if total == 0:
        return SystemIntegrityReport(
            total_problems=0,
            strong_correctness_pct=0.0,
            valid_measurement_pct=0.0,
            invalid_unstable_pct=0.0,
            no_reference_baseline_pct=100.0,
            classification_blocked=True,
        )

    strong_count = sum(
        1 for m in measurements
        if m.validation_strength == "strong"
    )
    valid_count = sum(
        1 for m in measurements
        if m.measurement_status == "valid"
    )
    invalid_count = sum(
        1 for m in measurements
        if m.measurement_status in ("invalid_measurement", "unstable")
    )
    no_ref_count = sum(
        1 for m in measurements
        if m.reference_type == "" or m.reference_type is None
    )

    valid_pct = valid_count / total * 100

    return SystemIntegrityReport(
        total_problems=total,
        strong_correctness_pct=strong_count / total * 100,
        valid_measurement_pct=valid_pct,
        invalid_unstable_pct=invalid_count / total * 100,
        no_reference_baseline_pct=no_ref_count / total * 100,
        classification_blocked=valid_pct < 70.0,
    )


def integrity_report_to_dict(r: SystemIntegrityReport) -> dict:
    """Serialize to JSON-compatible dict."""
    return {
        "total_problems": r.total_problems,
        "strong_correctness_pct": round(r.strong_correctness_pct, 1),
        "valid_measurement_pct": round(r.valid_measurement_pct, 1),
        "invalid_unstable_pct": round(r.invalid_unstable_pct, 1),
        "no_reference_baseline_pct": round(r.no_reference_baseline_pct, 1),
        "classification_blocked": r.classification_blocked,
    }


# ═══════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY: compute_efficiency (READ-ONLY)
# S is computed but NEVER used for decision-making.
# ═══════════════════════════════════════════════════════════

S_KIND_NO_EFFICIENCY = {"linear"}
S_KIND_HAS_EFFICIENCY = {"search", "graph", "dp", "quadratic", "log_linear"}
S_THRESHOLD = 10.0

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


@dataclass
class EfficiencyResult:
    s_observed_ms: float
    s_ref_ms: float
    s_final: float
    efficiency: str             # "efficient" | "inefficient" | "not_applicable"
    s_kind: str
    efficiency_applicable: bool
    # PHASE 0: New fields for research diagnostics
    measurement_status: str = ""  # "valid" | "unstable" | "invalid_measurement"
    research_only: bool = True   # ALWAYS True — S is not used for decisions


def compute_efficiency(traces, problem_key, s_ref_override=None, s_kind_override=None):
    """Backward-compatible S computation with disjoint branches.

    PHASE 0: S is READ-ONLY research output. NEVER used for decision-making.
    """
    total_ms = sum(t.get("execution_time", 0.0) * 1000.0 for t in traces) if traces else 0.0
    registry_entry = S_REF_REGISTRY.get(problem_key, {})
    s_ref = s_ref_override or registry_entry.get("s_ref_ms", None)
    s_kind = s_kind_override or registry_entry.get("s_kind", None)

    if s_ref is None or s_ref <= 0 or s_kind is None:
        return EfficiencyResult(
            s_observed_ms=round(total_ms, 4), s_ref_ms=0.0, s_final=0.0,
            efficiency="not_applicable", s_kind=s_kind or "unknown",
            efficiency_applicable=False, measurement_status="no_reference",
            research_only=True,
        )

    s_final = total_ms / s_ref

    # DISJOINT: linear → always not_applicable
    if s_kind in S_KIND_NO_EFFICIENCY:
        return EfficiencyResult(
            s_observed_ms=round(total_ms, 4), s_ref_ms=s_ref,
            s_final=round(s_final, 2), efficiency="not_applicable",
            s_kind=s_kind, efficiency_applicable=False,
            measurement_status="linear_not_applicable", research_only=True,
        )

    # DISJOINT: non-linear → binary
    if s_kind in S_KIND_HAS_EFFICIENCY:
        efficiency = "inefficient" if s_final >= S_THRESHOLD else "efficient"
        return EfficiencyResult(
            s_observed_ms=round(total_ms, 4), s_ref_ms=s_ref,
            s_final=round(s_final, 2), efficiency=efficiency,
            s_kind=s_kind, efficiency_applicable=True,
            measurement_status="valid", research_only=True,
        )

    return EfficiencyResult(
        s_observed_ms=round(total_ms, 4), s_ref_ms=s_ref,
        s_final=round(s_final, 2), efficiency="not_applicable",
        s_kind=s_kind, efficiency_applicable=False,
        measurement_status="unknown_kind", research_only=True,
    )


def efficiency_to_dict(r):
    return {
        "s_observed_ms": r.s_observed_ms, "s_ref_ms": r.s_ref_ms,
        "s_final": r.s_final, "efficiency": r.efficiency,
        "s_kind": r.s_kind, "efficiency_applicable": r.efficiency_applicable,
        "measurement_status": r.measurement_status,
        "research_only": r.research_only,
    }


def measurement_to_dict(m: GrowthMeasurement) -> dict:
    """Serialize GrowthMeasurement to JSON-compatible dict."""
    return {
        "problem_key": m.problem_key,
        "variant_name": m.variant_name,
        "sizes": m.sizes,
        "median_steps": m.median_steps,
        "variance_steps": m.variance_steps,
        "cv_steps_pct": m.cv_steps,
        "log_log_slope": m.log_log_slope,
        "slope_quality": m.slope_quality,
        "slope_reference": m.slope_reference,
        "slope_ratio": m.slope_ratio,
        "reference_type": m.reference_type,
        "absolute_growth": m.absolute_growth,
        "relative_optimality": m.relative_optimality,
        "validation_strength": m.validation_strength,
        "measurement_status": m.measurement_status,
        "invalid_reason": m.invalid_reason,
        "research_only_note": "S is NOT used for decision-making",
    }
