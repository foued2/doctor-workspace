"""
Test Executor — Execution-based Layer 2 for Doctor.

Runs solution code against curated test cases and verifies outputs.
Catches semantic bugs that structural analysis (Layer 1) cannot detect.

No API calls. No structural analysis. Pure execution + verification.
"""
from __future__ import annotations

import copy
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .execution_trace import run_test_with_trace
from ..grading.doctor_grader import (
    classify_failure_severity,
    classify_failure_type,
    classify_partial_vs_incorrect,
)


@dataclass
class TestCase:
    """A single test case with input, expected output, and optional label."""
    input: tuple                # positional args to the function
    expected: Any               # expected return value
    label: str = ""             # human-readable label (e.g., "all_negative")


@dataclass
class TestResult:
    """Result of running one test case."""
    label: str
    passed: bool
    got: Any = None
    expected: Any = None
    error: str = ""
    validator_passed: bool = None      # diagnostic only — not used for pass/fail
    validator_kind: str = None          # "validator_passed", "validator_failed", "no_validator"


@dataclass
class ExecutionReport:
    """Full report from executing a solution against a problem's test suite."""
    verdict: str                # "correct" | "partial" | "incorrect"
    pass_rate: float            # 0.0 to 1.0
    total: int
    passed: int
    results: List[TestResult] = field(default_factory=list)
    error: str = ""             # execution error (can't run code)
    evidence_score: float = None    # test coverage strength (from evidence score calibrator)
    failure_type: str = None    # "standard", "edge_only", or None (DEPRECATED)
    failure_ratio: float = None # failed_tests / total_tests
    severity: str = None        # "none" | "minor" | "moderate" | "severe"
    core_failures: int = 0      # count of core (non-edge) test failures
    edge_failures: int = 0      # count of edge test failures
    traces: List[dict] = field(default_factory=list)  # raw execution traces


# ===========================================================================
# Helper: build a linked list from a Python list (for merge_two_sorted_lists)
# ===========================================================================

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def make_list(vals: list) -> Optional[ListNode]:
    """Build a linked list from a Python list."""
    if not vals:
        return None
    head = ListNode(vals[0])
    curr = head
    for v in vals[1:]:
        curr.next = ListNode(v)
        curr = curr.next
    return head


def list_to_vals(head: Optional[ListNode]) -> list:
    """Convert a linked list to a Python list."""
    vals = []
    while head:
        vals.append(head.val)
        head = head.next
    return vals


# ===========================================================================
# TEST SUITES — loaded from registry (single source of truth)
# ===========================================================================

def _build_test_suites() -> Dict[str, List[TestCase]]:
    """Build TEST_SUITES from registry. Called once at module load."""
    from ..registry.problem_registry import get_problems

    suites: Dict[str, List[TestCase]] = {}
    for key, entry in get_problems().items():
        test_cases = entry.get("execution", {}).get("test_cases", [])
        suites[key] = [
            TestCase(
                input=_to_test_input(tc["input"], key),
                expected=tc["expected"],
                label=tc["label"],
            )
            for tc in test_cases
        ]
    return suites


def _to_test_input(raw_input, problem_key: str):
    """Convert a JSON-serialized test input to executable form.

    - For merge_two_sorted_lists: each list element becomes a ListNode.
      Result is a list (not tuple) since ListNodes are iterable.
    - For all other problems: recursively convert lists, wrap outer in tuple.
    """
    if problem_key == "merge_two_sorted_lists" and isinstance(raw_input, list):
        return [_maybe_list_to_listnode(x) if isinstance(x, list) else x for x in raw_input]
    if isinstance(raw_input, list):
        return tuple(_to_test_input(x, problem_key) for x in raw_input)
    return raw_input


def _maybe_list_to_listnode(obj):
    if isinstance(obj, list):
        return make_list(obj)
    return obj


def _maybe_to_listnode(obj, problem_key: str):
    if problem_key == "merge_two_sorted_lists" and isinstance(obj, list):
        return make_list(obj)
    if isinstance(obj, list):
        return [_maybe_to_listnode(x, problem_key) for x in obj]
    return obj


def _maybe_list_to_listnode(obj):
    if isinstance(obj, list):
        return make_list(obj)
    return obj


def _maybe_to_listnode(obj, problem_key: str):
    if problem_key == "merge_two_sorted_lists" and isinstance(obj, list) and not any(isinstance(x, list) for x in obj):
        return make_list(obj)
    if isinstance(obj, list):
        return [_maybe_to_listnode(x, problem_key) for x in obj]
    return obj


def _build_problem_key_map() -> Dict[str, str]:
    """Build PROBLEM_KEY_MAP from registry: display_name -> suite_key."""
    from ..registry.problem_registry import get_problems
    return {
        v.get("spec", {}).get("display_name", ""): k
        for k, v in get_problems().items()
        if v.get("spec", {}).get("display_name")
    }


TEST_SUITES: Dict[str, List[TestCase]] = _build_test_suites()
PROBLEM_KEY_MAP: Dict[str, str] = _build_problem_key_map()


# ===========================================================================
# Comparison helpers
# ===========================================================================

# OPTION A: Spec-oracle system. E (_results_equal) is the sole correctness
# oracle. Validators run for diagnostics only — they never affect pass/fail.

def _verify_with_validator(problem_key: str, got, test_input) -> tuple:
    """Verify output using a problem-specific validator.
    
    Returns (is_valid, kind) where kind is:
      - "validator_passed" — strong/partial validator confirmed correctness
      - "validator_failed" — validator detected incorrect output
      - "no_validator" — no validator exists for this problem
    """
    try:
        from ..validate.output_validators import validate_output
        # Build params dict from test_input for validators that need it
        params = _build_validator_params(test_input)
        result = validate_output(problem_key, got, params)
        if result[0]:  # valid
            return True, "validator_passed"
        else:
            return False, "validator_failed"
    except ImportError:
        # Validator module doesn't exist
        return None, "no_validator"
    except Exception:
        # Validator doesn't exist for this problem or failed to run
        return None, "no_validator"


def _build_validator_params(test_input: tuple) -> dict:
    """Build validator params dict from test input tuple.
    
    Different problems need different params. This maps common patterns.
    """
    if not test_input:
        return {}
    
    # N-Queens: (n,)
    if len(test_input) == 1 and isinstance(test_input[0], int):
        return {"n": test_input[0]}
    
    # Two Sum: (nums, target)
    if len(test_input) == 2 and isinstance(test_input[0], list):
        return {"nums": test_input[0], "target": test_input[1]}
    
    # Valid Parentheses: (string,)
    if len(test_input) == 1 and isinstance(test_input[0], str):
        return {"s": test_input[0]}
    
    # Container: (heights,)
    if len(test_input) == 1 and isinstance(test_input[0], list):
        return {"height": test_input[0]}
    
    # Trap Water: (heights,)
    if len(test_input) == 1 and isinstance(test_input[0], list):
        return {"height": test_input[0]}
    
    # Generic: pass as tuple
    return {"input": test_input}


def _results_equal(got, expected) -> bool:
    """Compare got vs expected, handling lists, floats, linked lists."""
    # Handle None linked list as empty list
    if got is None and expected == []:
        return True
    if expected is None and got == []:
        return True
    if isinstance(expected, list) and isinstance(got, list):
        # For N-Queens results: check if expected boards are valid solutions
        # Expected can be a single board that should be in got, or full set
        if expected and isinstance(expected[0], list) and expected[0] and isinstance(expected[0][0], str):
            got_set = set(tuple(board) for board in got if isinstance(board, list))
            # If expected has 1 board, check if it's in got (partial validation)
            if len(expected) == 1:
                return tuple(expected[0]) in got_set
            # If expected has multiple boards, check set equality
            exp_set = set(tuple(board) for board in expected if isinstance(board, list))
            return got_set == exp_set
        # For 3Sum/4Sum results: compare as sets of sorted tuples
        if expected and isinstance(expected[0], list):
            got_set = set(tuple(sorted(t)) for t in got if isinstance(t, list))
            exp_set = set(tuple(sorted(t)) for t in expected if isinstance(t, list))
            return got_set == exp_set
        return got == expected
    if isinstance(expected, float):
        return abs(got - expected) < 1e-9
    if isinstance(got, ListNode):
        return list_to_vals(got) == expected
    return got == expected


def _safe_exec(code: str) -> Optional[callable]:
    """Execute solution code and return the function, or None on error."""
    from ..normalize.solution_normalizer import normalize_solution, extract_function
    
    # Normalize GPT-generated solutions through the normalizer
    code = normalize_solution(code)
    
    return extract_function(code)


# ===========================================================================
# MAIN EXECUTOR
# ===========================================================================

class TestExecutor:

    def verify(self, problem_name: str, solution_code: str) -> ExecutionReport:
        """Execute solution against test cases and return verdict.

        Args:
            problem_name: LeetCode problem name (e.g., "Two Sum")
            solution_code: Python source code of the solution

        Returns:
            ExecutionReport with verdict, pass_rate, and per-test results.
        """
        # Map problem name to test suite key
        suite_key = PROBLEM_KEY_MAP.get(problem_name)
        if suite_key is None:
            return ExecutionReport(
                verdict="incorrect", pass_rate=0.0, total=0, passed=0,
                error=f"No test suite for problem: {problem_name}",
            )

        test_cases = TEST_SUITES.get(suite_key)
        if test_cases is None:
            return ExecutionReport(
                verdict="incorrect", pass_rate=0.0, total=0, passed=0,
                error=f"No test cases for suite key: {suite_key}",
            )

        # Extract function
        func = _safe_exec(solution_code)
        if func is None:
            return ExecutionReport(
                verdict="incorrect", pass_rate=0.0, total=len(test_cases), passed=0,
                error="Failed to parse/execute solution code",
            )

        # Run test cases using execution tracing
        results: List[TestResult] = []
        traces: List[dict] = []
        for tc in test_cases:
            trace = run_test_with_trace(func, tc.input, tc.expected)
            traces.append(trace)
            # OPTION A: Spec-oracle system. E is the sole correctness oracle.
            # Validator runs for diagnostics only — never affects pass/fail.
            validator_result, validator_kind = _verify_with_validator(
                problem_name, trace.get("output"), tc.input
            )

            # E = _results_equal is the ONLY correctness criterion
            if trace["error"] is not None:
                passed = False
            else:
                passed = _results_equal(trace["output"], tc.expected)

            results.append(TestResult(
                label=tc.label, passed=passed,
                got=trace["output"], expected=tc.expected,
                error=trace["error"].split("\n")[-2] if trace["error"] else "",
            ))
            # Store validator result for diagnostics (not used in pass/fail)
            results[-1].validator_passed = validator_result
            results[-1].validator_kind = validator_kind

        passed = sum(1 for r in results if r.passed)
        total = len(results)
        pass_rate = passed / total if total > 0 else 0.0

        # ── FIX 1: Evidence-based confidence ─────────────────────────
        # Determine if test suite covers edge cases
        edge_labels = {"empty", "single", "negative", "overflow", "edge", "zero",
                       "no_first_two", "self_element_reuse", "unsorted",
                       "subtractive", "wrong_order", "unclosed", "both_empty",
                       "one_empty", "interleaved", "one_larger",
                       "no_prefix", "empty_string", "different_lengths",
                       "not_found", "single_match", "at_end", "empty_needle",
                       "single_not_found", "two_equal", "small",
                       "single_char", "numrows_1", "trailing_zero",
                       "leading_spaces_negative", "overflow_negative",
                       "odd_total", "even_total", "first_empty", "all_zero",
                       "first_empty_even", "too_short", "star_repeat",
                       "star_all", "star_empty", "both_empty",
                       "all_same", "n4_solutions", "wrong_char",
                       "delete_all", "insert_all",
                       "all_negative", "basic_odd", "basic_even",
                       "two_no_palindrome", "full_string",
                       "nested", "all_types"}
        has_edge_cases = any(tc.label.lower() in edge_labels for tc in test_cases)

        from ..grading.confidence_calibrator import compute_evidence_score
        calibrated_evidence = compute_evidence_score(
            tests_passed=passed,
            tests_total=total,
            has_edge_cases=has_edge_cases,
        )

        # ── FIX 3: Partial redefinition by failure pattern ───────────
        # Build failure reasons from failed test labels
        failed_labels = [r.label for r in results if not r.passed]
        failed_test_names = failed_labels  # same list, used for severity

        if pass_rate == 1.0:
            verdict = "correct"
            failure_type = None
            failure_ratio = 0.0
            severity = "none"
            core_failures = 0
            edge_failures = 0
        else:
            failure_ratio = len(failed_labels) / total if total > 0 else 1.0
            verdict = classify_partial_vs_incorrect(failed_labels)
            failure_type = classify_failure_type(failed_labels)
            severity, core_failures, edge_failures = classify_failure_severity(
                failure_ratio, failed_test_names
            )

        return ExecutionReport(
            verdict=verdict,
            pass_rate=round(pass_rate, 4),
            total=total,
            passed=passed,
            results=results,
            evidence_score=calibrated_evidence,
            failure_type=failure_type,
            failure_ratio=round(failure_ratio, 4),
            severity=severity,
            core_failures=core_failures,
            edge_failures=edge_failures,
            traces=traces,
        )
