"""
Test Ingestion Pipeline — Dataset Construction System
======================================================
Purpose: Transform a problem specification into a validated TEST_SUITES entry.

HARD CONSTRAINT: This pipeline MUST NOT:
  - modify grading logic
  - access test_executor.py correctness paths
  - influence _results_equal
  - define or modify correctness rules

It is a compile-time dataset constructor only.
"""
from __future__ import annotations

import hashlib
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple


# ═══════════════════════════════════════════════════════════════
# SCHEMA DEFINITIONS
# ═══════════════════════════════════════════════════════════════

@dataclass
class ProblemSpec:
    """Normalized problem specification."""
    problem_id: str                  # canonical identifier (e.g., "two_sum")
    display_name: str                # human-readable name (e.g., "Two Sum")
    description: str                 # problem statement
    input_schema: Dict[str, str]     # {param_name: type_description}
    output_type: str                 # type description of return value
    constraints: Dict[str, Any]      # problem constraints (n ranges, etc.)
    reference_solution: Optional[Callable] = None   # human-approved reference
    reference_approved: bool = False  # must be explicitly set to True


@dataclass
class TestCaseSpec:
    """A single test case with metadata."""
    input: tuple
    expected: Any
    label: str
    source: str = "manual"           # "manual" | "generated" | "boundary"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IngestionResult:
    """Result of ingesting a problem."""
    problem_id: str
    test_cases: List[TestCaseSpec]
    validation_errors: List[str]
    warnings: List[str]
    integrity_hash: str              # SHA-256 of all test cases


# ═══════════════════════════════════════════════════════════════
# STAGE 1: SCHEMA NORMALIZATION
# ═══════════════════════════════════════════════════════════════

def parse_problem(
    problem_id: str,
    display_name: str,
    description: str,
    input_schema: Dict[str, str],
    output_type: str,
    constraints: Dict[str, Any],
    reference_solution: Optional[Callable] = None,
) -> ProblemSpec:
    """Create a normalized problem specification.

    This is pure data construction — no execution, no correctness checks.
    """
    return ProblemSpec(
        problem_id=problem_id,
        display_name=display_name,
        description=description,
        input_schema=input_schema,
        output_type=output_type,
        constraints=constraints,
        reference_solution=reference_solution,
        reference_approved=False,  # must be explicitly approved separately
    )


def approve_reference(spec: ProblemSpec) -> ProblemSpec:
    """Human approves the reference implementation.

    This is an explicit action — no automatic approval.
    """
    if spec.reference_solution is None:
        raise ValueError("No reference solution to approve")
    spec.reference_approved = True
    return spec


# ═══════════════════════════════════════════════════════════════
# STAGE 2: EDGE CASE GENERATION
# ═══════════════════════════════════════════════════════════════

def generate_boundary_cases(
    spec: ProblemSpec,
    reference_fn: Callable,
    boundary_inputs: List[tuple],
) -> List[TestCaseSpec]:
    """Generate boundary/edge test cases from a reference function.

    The reference function MUST be:
    - single-source (no competing implementations)
    - human-approved
    - deterministic (pure function)

    Expected outputs are derived by construction — not by voting or consensus.
    """
    if not spec.reference_approved:
        raise ValueError(
            f"Reference solution not approved for {spec.problem_id}. "
            "Call approve_reference() before generating test cases."
        )

    cases = []
    for boundary_input in boundary_inputs:
        expected = reference_fn(*boundary_input)
        label = boundary_input_to_label(boundary_input, spec.constraints)
        cases.append(TestCaseSpec(
            input=boundary_input,
            expected=expected,
            label=label,
            source="boundary",
            metadata={"constraint": "boundary_value"},
        ))
    return cases


def boundary_input_to_label(boundary_input: tuple, constraints: Dict[str, Any]) -> str:
    """Generate a human-readable label for a boundary input.

    Uses constraint metadata and input characteristics to produce descriptive labels.
    """
    labels = []

    for i, val in enumerate(boundary_input):
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            # Check against known constraint boundaries
            for cname, cval in constraints.items():
                if isinstance(cval, dict):
                    if "min_length" in cval and isinstance(val, int) and val == cval["min_length"]:
                        labels.append(f"min_len")
                    if "max_length" in cval and isinstance(val, int) and val == cval["max_length"]:
                        labels.append(f"max_len")
                    if "min" in cval and val == cval["min"]:
                        labels.append(f"min_{cname}")
                    if "max" in cval and val == cval["max"]:
                        labels.append(f"max_{cname}")
            # Heuristic: check for zeros, extremes
            if val == 0:
                labels.append("zero")
            if abs(val) >= 10**8:
                labels.append("extreme")

        if isinstance(val, list):
            if len(val) == 0:
                labels.append("empty")
            elif len(val) == 1:
                labels.append("single_element")
            elif len(val) == 2:
                labels.append("min_length")

    if not labels:
        return "boundary"

    # Deduplicate and join
    return "_".join(sorted(set(labels)))


# ═══════════════════════════════════════════════════════════════
# STAGE 3: INTEGRITY VALIDATION
# ═══════════════════════════════════════════════════════════════

def validate_schema(test_cases: List[TestCaseSpec], spec: ProblemSpec) -> List[str]:
    """Validate that all test cases conform to the problem schema.

    Returns list of validation errors (empty = all valid).
    """
    errors = []
    for i, tc in enumerate(test_cases):
        # Check input arity matches schema
        if len(tc.input) != len(spec.input_schema):
            errors.append(
                f"TestCase {i} ({tc.label}): input arity {len(tc.input)} != "
                f"expected {len(spec.input_schema)}"
            )

        # Check input types
        for j, (param_name, type_desc) in enumerate(spec.input_schema.items()):
            val = tc.input[j] if j < len(tc.input) else None
            if not _check_type(val, type_desc):
                errors.append(
                    f"TestCase {i} ({tc.label}): input[{j}] ({param_name}) "
                    f"type mismatch: expected {type_desc}, got {type(val).__name__}"
                )

        # Check output type
        if not _check_type(tc.expected, spec.output_type):
            errors.append(
                f"TestCase {i} ({tc.label}): output type mismatch: "
                f"expected {spec.output_type}, got {type(tc.expected).__name__}"
            )

        # Check label is non-empty
        if not tc.label:
            errors.append(f"TestCase {i}: empty label")

    return errors


def validate_determinism(reference_fn: Callable, test_inputs: List[tuple], n_runs: int = 3) -> List[str]:
    """Verify that the reference function produces identical output across runs.

    Returns list of errors (empty = deterministic).
    """
    errors = []
    for inp in test_inputs:
        outputs = [reference_fn(*inp) for _ in range(n_runs)]
        if not all(o == outputs[0] for o in outputs):
            errors.append(
                f"Non-deterministic output for input {inp}: "
                f"got {len(set(str(o) for o in outputs))} distinct outputs"
            )
    return errors


def detect_duplicates(test_cases: List[TestCaseSpec]) -> List[str]:
    """Detect duplicate test cases (same input).

    Returns list of warnings (empty = no duplicates).
    """
    warnings = []
    seen_inputs = {}
    for i, tc in enumerate(test_cases):
        key = str(tc.input)
        if key in seen_inputs:
            warnings.append(
                f"Duplicate input at index {i} ({tc.label}): "
                f"same as index {seen_inputs[key]} ({test_cases[seen_inputs[key]].label})"
            )
        else:
            seen_inputs[key] = i
    return warnings


def _check_type(value: Any, type_desc: str) -> bool:
    """Check if a value matches a type description string."""
    type_map = {
        "int": lambda v: isinstance(v, int) and not isinstance(v, bool),
        "float": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "bool": lambda v: isinstance(v, bool),
        "str": lambda v: isinstance(v, str),
        "list": lambda v: isinstance(v, list),
        "list[int]": lambda v: isinstance(v, list) and all(isinstance(x, int) and not isinstance(x, bool) for x in v),
        "list[str]": lambda v: isinstance(v, list) and all(isinstance(x, str) for x in v),
        "list[list[str]]": lambda v: isinstance(v, list) and all(isinstance(r, list) and all(isinstance(c, str) for c in r) for r in v),
        "list[list[int]]": lambda v: isinstance(v, list) and all(isinstance(r, list) and all(isinstance(c, int) and not isinstance(c, bool) for c in r) for r in v),
        "tuple": lambda v: isinstance(v, tuple),
        "dict": lambda v: isinstance(v, dict),
        "None": lambda v: v is None,
    }
    checker = type_map.get(type_desc)
    if checker is None:
        return True  # unknown type desc, skip check
    return checker(value)


# ═══════════════════════════════════════════════════════════════
# STAGE 4: INTEGRITY HASH
# ═══════════════════════════════════════════════════════════════

def compute_integrity_hash(test_cases: List[TestCaseSpec]) -> str:
    """Compute SHA-256 hash of all test cases for integrity tracking."""
    content = ""
    for tc in sorted(test_cases, key=lambda t: t.label):
        content += f"{tc.label}:{tc.input}:{tc.expected}\n"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


# ═══════════════════════════════════════════════════════════════
# MAIN INGESTION FUNCTION
# ═══════════════════════════════════════════════════════════════

def ingest_problem(
    spec: ProblemSpec,
    manual_cases: List[TestCaseSpec],
    boundary_inputs: Optional[List[tuple]] = None,
) -> IngestionResult:
    """Ingest a problem specification into a validated TEST_SUITES entry.

    Data flow:
      1. Schema normalization (already done in spec)
      2. Edge case generation (from reference function + boundary inputs)
      3. Integrity validation (types, determinism, duplicates)
      4. Merge and hash

    This function does NOT:
      - modify grading logic
      - influence _results_equal
      - evaluate solution correctness
      - participate in scoring
    """
    errors = []
    warnings = []

    # Combine manual and generated cases
    all_cases = list(manual_cases)

    # Stage 2: Generate boundary cases if reference exists and boundary inputs provided
    if spec.reference_approved and spec.reference_solution and boundary_inputs:
        boundary_cases = generate_boundary_cases(
            spec, spec.reference_solution, boundary_inputs
        )
        all_cases.extend(boundary_cases)

    # Stage 3: Integrity validation
    schema_errors = validate_schema(all_cases, spec)
    errors.extend(schema_errors)

    # Determinism check (only if reference exists)
    if spec.reference_approved and spec.reference_solution:
        test_inputs = [tc.input for tc in all_cases]
        det_errors = validate_determinism(spec.reference_solution, test_inputs)
        errors.extend(det_errors)

    # Duplicate detection
    dup_warnings = detect_duplicates(all_cases)
    warnings.extend(dup_warnings)

    # Stage 4: Integrity hash
    integrity_hash = compute_integrity_hash(all_cases)

    return IngestionResult(
        problem_id=spec.problem_id,
        test_cases=all_cases,
        validation_errors=errors,
        warnings=warnings,
        integrity_hash=integrity_hash,
    )


# ═══════════════════════════════════════════════════════════════
# EXPORT TO TEST_SUITES FORMAT
# ═══════════════════════════════════════════════════════════════

def to_test_cases(result: IngestionResult) -> List[dict]:
    """Convert ingestion result to test_executor.TestCase format.

    This is a pure data transformation — no logic, no correctness checks.
    """
    from doctor.core.test_executor import TestCase

    test_cases = []
    for tc in result.test_cases:
        test_cases.append(TestCase(
            input=tc.input,
            expected=tc.expected,
            label=tc.label,
        ))
    return test_cases


# ═══════════════════════════════════════════════════════════════
# SELF-TEST
# ═══════════════════════════════════════════════════════════════

def _self_test():
    """Validate the ingestion pipeline on Two Sum."""

    # Reference solution (human-approved, single-source, deterministic)
    def two_sum_reference(nums, target):
        seen = {}
        for i, n in enumerate(nums):
            if target - n in seen:
                return [seen[target - n], i]
            seen[n] = i
        return []

    # Create problem spec
    spec = parse_problem(
        problem_id="two_sum",
        display_name="Two Sum",
        description="Return indices of two numbers that add up to target.",
        input_schema={"nums": "list[int]", "target": "int"},
        output_type="list[int]",
        constraints={
            "nums": {"min_length": 2, "max_length": 10000},
            "target": {"min": -10**9, "max": 10**9},
        },
        reference_solution=two_sum_reference,
    )

    # Approve reference
    approve_reference(spec)

    # Manual test cases (existing curated cases)
    manual = [
        TestCaseSpec(([2, 7, 11, 15], 9), [0, 1], "basic", "manual"),
        TestCaseSpec(([3, 2, 4], 6), [1, 2], "no_first_two", "manual"),
        TestCaseSpec(([3, 3], 6), [0, 1], "self_element_reuse", "manual"),
        TestCaseSpec(([-1, -2, -3, -4, -5], -8), [2, 4], "negative_numbers", "manual"),
        TestCaseSpec(([1, 5, 3, 7], 10), [2, 3], "unsorted", "manual"),
    ]

    # Boundary inputs for edge case generation
    boundaries = [
        ([1, 2], 3),           # min length
        ([10**9, -10**9], 0),  # extreme values
        ([0, 0], 0),           # zeros
    ]

    # Ingest
    result = ingest_problem(spec, manual, boundaries)

    print(f"Problem: {result.problem_id}")
    print(f"Test cases: {len(result.test_cases)}")
    print(f"Validation errors: {len(result.validation_errors)}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Integrity hash: {result.integrity_hash}")

    if result.validation_errors:
        print("ERRORS:")
        for e in result.validation_errors:
            print(f"  - {e}")
    if result.warnings:
        print("WARNINGS:")
        for w in result.warnings:
            print(f"  - {w}")

    # Convert to TestCase format
    test_cases = to_test_cases(result)
    print(f"\nConverted to {len(test_cases)} TestCase objects")
    for tc in test_cases:
        print(f"  {tc.label}: input={tc.input}, expected={tc.expected}")

    # Verify no errors
    assert len(result.validation_errors) == 0, f"Validation errors: {result.validation_errors}"
    assert len(result.test_cases) == 8  # 5 manual + 3 boundary
    assert result.integrity_hash  # non-empty

    print("\nSelf-test PASSED ✓")


if __name__ == "__main__":
    _self_test()
