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

from doctor.execution_trace import run_test_with_trace


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
# TEST SUITES — 29 LeetCode problems
# Each suite has 4-6 tests targeting: basic, edge, and subtle bugs.
# ===========================================================================
TEST_SUITES: Dict[str, List[TestCase]] = {
    # ── Easy (9) ──────────────────────────────────────────────────────────
    "two_sum": [
        TestCase(([2, 7, 11, 15], 9), [0, 1], "basic"),
        TestCase(([3, 2, 4], 6), [1, 2], "no_first_two"),
        TestCase(([3, 3], 6), [0, 1], "self_element_reuse"),
        TestCase(([-1, -2, -3, -4, -5], -8), [2, 4], "negative_numbers"),
        TestCase(([1, 5, 3, 7], 10), [2, 3], "unsorted"),
    ],
    "palindrome_number": [
        TestCase((121,), True, "basic_positive"),
        TestCase((-121,), False, "negative"),
        TestCase((10,), False, "trailing_zero"),
        TestCase((0,), True, "zero"),
        TestCase((1221,), True, "even_length"),
    ],
    "roman_to_integer": [
        TestCase(("III",), 3, "basic"),
        TestCase(("IV",), 4, "subtractive_IV"),
        TestCase(("IX",), 9, "subtractive_IX"),
        TestCase(("LVIII",), 58, "mixed"),
        TestCase(("MCMXCIV",), 1994, "complex"),
    ],
    "longest_common_prefix": [
        TestCase((["flower", "flow", "flight"],), "fl", "basic"),
        TestCase((["dog", "racecar", "car"],), "", "no_prefix"),
        TestCase((["a"],), "a", "single"),
        TestCase((["", "b"],), "", "empty_string"),
        TestCase((["ab", "a"],), "a", "different_lengths"),
    ],
    "valid_parentheses": [
        TestCase(("()",), True, "basic"),
        TestCase(("()[]{}",), True, "all_types"),
        TestCase(("(]",), False, "wrong_type"),
        TestCase(("([)]",), False, "wrong_order"),
        TestCase(("(",), False, "unclosed"),
        TestCase(("{[]}",), True, "nested"),
        TestCase(("",), True, "empty"),
    ],
    "merge_two_sorted_lists": [
        TestCase(
            (make_list([1, 2, 4]), make_list([1, 3, 4])),
            [1, 1, 2, 3, 4, 4], "basic",
        ),
        TestCase((make_list([]), make_list([])), [], "both_empty"),
        TestCase((make_list([]), make_list([0])), [0], "one_empty"),
        TestCase((make_list([1, 3, 5]), make_list([2, 4, 6])), [1, 2, 3, 4, 5, 6], "interleaved"),
        TestCase((make_list([5]), make_list([1, 2, 3])), [1, 2, 3, 5], "one_larger"),
    ],
    "remove_duplicates": [
        TestCase(([0, 0, 1, 1, 1, 2, 2, 3, 3, 4],), 5, "basic"),
        TestCase(([1, 1, 2],), 2, "small"),
        TestCase(([0, 1, 2],), 3, "no_duplicates"),
        TestCase(([1],), 1, "single"),
        TestCase(([],), 0, "empty"),
    ],
    "strStr": [
        TestCase(("hello", "ll"), 2, "basic"),
        TestCase(("aaaaa", "bba"), -1, "not_found"),
        TestCase(("", ""), 0, "both_empty"),
        TestCase(("a", "a"), 0, "single_match"),
        TestCase(("abc", "c"), 2, "at_end"),
        TestCase(("abc", ""), 0, "empty_needle"),
    ],
    "search_insert": [
        TestCase(([1, 3, 5, 6], 5), 2, "found"),
        TestCase(([1, 3, 5, 6], 2), 1, "not_found_middle"),
        TestCase(([1, 3, 5, 6], 7), 4, "not_found_end"),
        TestCase(([1, 3, 5, 6], 0), 0, "not_found_start"),
        TestCase(([1], 0), 0, "single_not_found"),
    ],
    # ── Medium (10) ───────────────────────────────────────────────────────
    "longest_palindrome": [
        TestCase(("babad",), "bab", "basic_odd"),  # or "aba"
        TestCase(("cbbd",), "bb", "basic_even"),
        TestCase(("a",), "a", "single"),
        TestCase(("ac",), "a", "two_no_palindrome"),  # or "c"
        TestCase(("abcba",), "abcba", "full_string"),
        # Additional LPS edge cases
        TestCase(("abba",), "abba", "basic_even"),
        TestCase(("aabbaa",), "aabbaa", "mixed"),
        TestCase(("abacdfgdcaba",), "aba", "no_repeat_trap"),
    ],
    "zigzag_conversion": [
        TestCase(("PAYPALISHIRING", 3), "PAHNAPLSIIGYIR", "basic_3rows"),
        TestCase(("PAYPALISHIRING", 4), "PINALSIGYAHRPI", "basic_4rows"),
        TestCase(("A", 1), "A", "single_char"),
        TestCase(("AB", 1), "AB", "numrows_1"),
        TestCase(("ABC", 2), "ACB", "basic_2rows"),
    ],
    "reverse_integer": [
        TestCase((123,), 321, "basic_positive"),
        TestCase((-123,), -321, "negative"),
        TestCase((120,), 21, "trailing_zero"),
        TestCase((0,), 0, "zero"),
        TestCase((1534236469,), 0, "overflow"),  # reverses to 9646324351 > 2^31-1
    ],
    "string_to_integer": [
        TestCase(("42",), 42, "basic"),
        TestCase(("   -42",), -42, "leading_spaces_negative"),
        TestCase(("4193 with words",), 4193, "trailing_text"),
        TestCase(("words and 987",), 0, "leading_text"),
        TestCase(("-91283472332",), -2147483648, "overflow_negative"),
        TestCase(("",), 0, "empty"),
    ],
    "max_area": [
        TestCase(([1, 8, 6, 2, 5, 4, 8, 3, 7],), 49, "basic"),
        TestCase(([1, 1],), 1, "two_equal"),
        TestCase(([4, 3, 2, 1, 4],), 16, "symmetric"),
        TestCase(([1, 2, 1],), 2, "small"),
    ],
    "int_to_roman": [
        TestCase((3,), "III", "basic"),
        TestCase((58,), "LVIII", "mixed"),
        TestCase((1994,), "MCMXCIV", "subtractive"),
        TestCase((1,), "I", "single"),
        TestCase((3999,), "MMMCMXCIX", "max"),
    ],
    "three_sum": [
        TestCase(([-1, 0, 1, 2, -1, -4],), [[-1, -1, 2], [-1, 0, 1]], "basic"),
        TestCase(([],), [], "empty"),
        TestCase(([0],), [], "single"),
        TestCase(([0, 0, 0],), [[0, 0, 0]], "all_zero"),
        TestCase(([1, 2, -2, -1],), [], "no_triplets"),
    ],
    "letter_combinations": [
        TestCase(("23",), ["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"], "basic"),
        TestCase(("",), [], "empty"),
        TestCase(("2",), ["a", "b", "c"], "single"),
        TestCase(("7",), ["p", "q", "r", "s"], "four_letters"),
    ],
    "four_sum": [
        TestCase(([1, 0, -1, 0, -2, 2], 0), [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]], "basic"),
        TestCase(([2, 2, 2, 2, 2], 8), [[2, 2, 2, 2]], "all_same"),
        TestCase(([], 0), [], "empty"),
        TestCase(([0], 0), [], "single"),
    ],
    "generate_parenthesis": [
        TestCase((3,), ["((()))", "(()())", "(())()", "()(())", "()()()"], "basic"),
        TestCase((1,), ["()"], "single"),
        TestCase((0,), [], "zero"),
        TestCase((2,), ["(())", "()()"], "two"),
    ],
    # ── Hard (10) ─────────────────────────────────────────────────────────
    "find_median_sorted_arrays": [
        TestCase(([1, 3], [2]), 2.0, "odd_total"),
        TestCase(([1, 2], [3, 4]), 2.5, "even_total"),
        TestCase(([], [1]), 1.0, "first_empty"),
        TestCase(([0, 0], [0, 0]), 0.0, "all_zero"),
        TestCase(([], [2, 3]), 2.5, "first_empty_even"),
    ],
    "regular_expression_matching": [
        TestCase(("aa", "a"), False, "too_short"),
        TestCase(("aa", "a*"), True, "star_repeat"),
        TestCase(("ab", ".*"), True, "dot_star"),
        TestCase(("mississippi", "mis*is*p*."), False, "complex"),
        TestCase(("", ".*"), True, "empty_match"),
        TestCase(("a", "ab*"), True, "optional_b"),
    ],
    "trap": [
        TestCase(([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],), 6, "basic"),
        TestCase(([4, 2, 0, 3, 2, 5],), 9, "tall"),
        TestCase(([],), 0, "empty"),
        TestCase(([1],), 0, "single"),
        TestCase(([1, 2, 3],), 0, "ascending"),
    ],
    "first_missing_positive": [
        TestCase(([1, 2, 0],), 3, "basic"),
        TestCase(([3, 4, -1, 1],), 2, "with_negative"),
        TestCase(([7, 8, 9, 11, 12],), 1, "all_large"),
        TestCase(([],), 1, "empty"),
        TestCase(([1],), 2, "single"),
    ],
    "solve_n_queens": [
        TestCase((1,), [["Q"]], "single"),
        TestCase((0,), [[]], "zero"),
        TestCase((2,), [], "n2_no_solutions"),
        TestCase((3,), [], "n3_no_solutions"),
        TestCase((4,), [[".Q..", "...Q", "Q...", "..Q."], ["..Q.", "Q...", "...Q", ".Q.."]], "n4_solutions"),
        TestCase((5,), [["Q....", "..Q..", "....Q", ".Q...", "...Q."]], "n5_board1"),
        TestCase((5,), [["Q....", "...Q.", ".Q...", "....Q", "..Q.."]], "n5_board2"),
        TestCase((6,), [[".Q....", "...Q..", ".....Q", "Q.....", "..Q...", "....Q."]], "n6_board1"),
        TestCase((6,), [["..Q...", ".....Q", ".Q....", "....Q.", "Q.....", "...Q.."]], "n6_board2"),
    ],
    "wildcard_matching": [
        TestCase(("aa", "a"), False, "too_short"),
        TestCase(("aa", "*"), True, "star_all"),
        TestCase(("cb", "?a"), False, "wrong_char"),
        TestCase(("adceb", "*a*b"), True, "complex"),
        TestCase(("", "*"), True, "star_empty"),
        TestCase(("", ""), True, "both_empty"),
    ],
    "min_distance": [
        TestCase(("horse", "ros"), 3, "basic"),
        TestCase(("intention", "execution"), 5, "long"),
        TestCase(("", ""), 0, "both_empty"),
        TestCase(("a", ""), 1, "delete_all"),
        TestCase(("", "abc"), 3, "insert_all"),
    ],
    "min_window": [
        TestCase(("ADOBECODEBANC", "ABC"), "BANC", "basic"),
        TestCase(("a", "a"), "a", "single"),
        TestCase(("a", "aa"), "", "not_found"),
        TestCase(("ab", "a"), "a", "substring"),
    ],
    "largest_rectangle_area": [
        TestCase(([2, 1, 5, 6, 2, 3],), 10, "basic"),
        TestCase(([2, 4],), 4, "two_bars"),
        TestCase(([],), 0, "empty"),
        TestCase(([1, 1],), 2, "equal"),
        TestCase(([1],), 1, "single"),
    ],
    "max_sliding_window": [
        TestCase(([1, 3, -1, -3, 5, 3, 6, 7], 3), [3, 3, 5, 5, 6, 7], "basic"),
        TestCase(([1, -1], 1), [1, -1], "k1"),
        TestCase(([1], 1), [1], "single"),
        TestCase(([9, 11], 2), [11], "k_equals_len"),
    ],
}


# ===========================================================================
# Problem → test suite key mapping
# ===========================================================================
PROBLEM_KEY_MAP = {
    "Two Sum": "two_sum",
    "Palindrome Number": "palindrome_number",
    "Roman to Integer": "roman_to_integer",
    "Longest Common Prefix": "longest_common_prefix",
    "Valid Parentheses": "valid_parentheses",
    "Merge Two Sorted Lists": "merge_two_sorted_lists",
    "Remove Duplicates from Sorted Array": "remove_duplicates",
    "Implement strStr()": "strStr",
    "Search Insert Position": "search_insert",
    "Longest Palindromic Substring": "longest_palindrome",
    "Zigzag Conversion": "zigzag_conversion",
    "Reverse Integer": "reverse_integer",
    "String to Integer (atoi)": "string_to_integer",
    "Container With Most Water": "max_area",
    "Integer to Roman": "int_to_roman",
    "3Sum": "three_sum",
    "Letter Combinations of a Phone Number": "letter_combinations",
    "4Sum": "four_sum",
    "Generate Parentheses": "generate_parenthesis",
    "Median of Two Sorted Arrays": "find_median_sorted_arrays",
    "Regular Expression Matching": "regular_expression_matching",
    "Trapping Rain Water": "trap",
    "First Missing Positive": "first_missing_positive",
    "N-Queens": "solve_n_queens",
    "Wildcard Matching": "wildcard_matching",
    "Edit Distance": "min_distance",
    "Minimum Window Substring": "min_window",
    "Largest Rectangle in Histogram": "largest_rectangle_area",
    "Sliding Window Maximum": "max_sliding_window",
}


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
        from doctor.output_validators import validate_output
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
    from doctor.solution_normalizer import normalize_solution, extract_function
    
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

        from doctor.confidence_calibrator import compute_evidence_score
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
            # Compute failure ratio and severity
            failure_ratio = len(failed_labels) / total if total > 0 else 1.0
            from doctor.doctor_grader import classify_failure_severity
            severity, core_failures, edge_failures = classify_failure_severity(
                failure_ratio, failed_test_names,
            )
            # Legacy classification (kept for backward compatibility)
            from doctor.doctor_grader import classify_failure_type
            failure_type = classify_failure_type(failed_labels)
            # Verdict uses pattern-based classification (partial vs incorrect by label semantics)
            from doctor.doctor_grader import classify_partial_vs_incorrect
            verdict = classify_partial_vs_incorrect(failed_labels)

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
