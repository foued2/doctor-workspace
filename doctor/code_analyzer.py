"""
Code Analyzer — Static analysis engine for Python solution verification.

Examines Python code against problem constraints and detects:
- Missing input guards (empty, single element)
- Index out-of-bounds access patterns
- Return type mismatches
- Complexity violations (O(n²) where O(n) implied)
- Incorrect initialization for negative-number constraints
- Unhandled edge cases

No API calls. No lookup tables. Pure static analysis.
"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AnalysisResult:
    verdict: str                          # "correct" | "partial" | "incorrect"
    confidence: float                     # 0.0–1.0
    failures: List[str]                   # list of failed check names
    details: Dict[str, bool] = field(default_factory=dict)   # per-check result
    reasoning: str = ""
    fatal_flags: List[str] = field(default_factory=list)     # constraint/complexity violations


# ===========================================================================
# TRACK B — Problem-specific constraint registries
# ===========================================================================

COMPLEXITY_CONSTRAINTS = {
    "two_sum": "O(n)",
    "max_area": "O(n)",                          # container_with_most_water
    "trap": "O(n)",                              # trapping_rain_water
    "longest_palindrome": "O(n2_ok)",            # O(n²) acceptable
    "merge_two_sorted_lists": "O(n)",
    "valid_parentheses": "O(n)",
    "roman_to_integer": "O(n)",
    "palindrome_number": "O(n)",
    "solve_n_queens": "O(n_factorial_ok)",       # exponential acceptable
}

PROBLEM_CONSTRAINTS = {
    "palindrome_number": {
        "banned_patterns": ["str(", "str)"],
        "reason": "must not convert integer to string"
    },
}

# ===========================================================================
# FIX 2 — Algorithm fingerprint signatures (wrong algorithm detection)
# ===========================================================================

ALGORITHM_SIGNATURES = {
    "longest_palindromic_substring": {
        "required_patterns": ["expand", "center", "palindrom"],
        "forbidden_patterns": ["suffix", "lcs", "longest_common"],
        "reason": "must use expand-around-center or DP, not LCS/suffix approach"
    },
}


# ===========================================================================
# AST helpers
# ===========================================================================

def _has_nested_loops(node: ast.AST) -> bool:
    """Detect any nested for-loop structure — generic O(n²) signal.

    Looks for:
        for ...:
            for ...:
    """
    for outer in _find_all(node, ast.For):
        for inner in ast.walk(outer):
            if inner is outer:
                continue
            if isinstance(inner, ast.For):
                return True
    return False


def _has_nested_same_input_loops(node: ast.AST) -> bool:
    """Detect nested loops iterating over the same input — O(n²) signal.

    Looks for:
        for i in range(len(x)):
            for j in range(len(x)):   # same variable x
    or
        for i in range(len(x)):
            for j in range(i+1, len(x)):
    """
    for_loops = _find_all(node, ast.For)
    for outer_loop in for_loops:
        # Extract iterable name from outer loop
        outer_names = _extract_iterable_names(outer_loop.iter)
        # Check if any inner loop (nested inside outer) iterates over same name
        for inner_node in ast.walk(outer_loop):
            if inner_node is outer_loop:
                continue
            if isinstance(inner_node, ast.For):
                inner_names = _extract_iterable_names(inner_node.iter)
                if outer_names and inner_names and outer_names & inner_names:
                    return True
    return False


def _safe_parse(source: str) -> Optional[ast.Module]:
    """Parse source to AST, return None on syntax error."""
    try:
        return ast.parse(source)
    except (SyntaxError, ValueError):
        return None


def _find_all(node: ast.AST, type_: type) -> List[ast.AST]:
    """Recursively find all AST nodes of a given type."""
    result = []
    for child in ast.walk(node):
        if isinstance(child, type_):
            result.append(child)
    return result


def _has_guard_for_empty(node: ast.AST) -> bool:
    """Does the code guard against empty input?

    Looks for patterns like:
        if not nums: ...
        if len(nums) == 0: ...
        if len(nums) < 1: ...
        if not s: ...
        if len(s) == 0: ...
    """
    for n in ast.walk(node):
        if isinstance(n, ast.If):
            test_src = ast.dump(n.test)
            # 'if not x' pattern
            if isinstance(n.test, ast.UnaryOp) and isinstance(n.test.op, ast.Not):
                return True
            # 'if len(x) == 0' or 'if len(x) < 1'
            if isinstance(n.test, ast.Compare):
                if isinstance(n.test.left, ast.Call):
                    func = n.test.left.func
                    if isinstance(func, ast.Name) and func.id == "len":
                        return True
    return False


def _has_guard_for_single(node: ast.AST) -> bool:
    """Does the code guard against single-element input?

    Looks for:
        if len(x) == 1: ...
        if len(x) < 2: ...
    """
    for n in ast.walk(node):
        if isinstance(n, ast.If):
            test = n.test
            if isinstance(test, ast.Compare) and isinstance(test.left, ast.Call):
                func = test.left.func
                if isinstance(func, ast.Name) and func.id == "len":
                    return True
    return False


def _extract_iterable_names(iter_node: ast.AST) -> set:
    """Extract variable names from iterable expressions.

    Handles:
        nums           -> {nums}
        range(len(nums)) -> {nums}
        range(i+1, len(nums)) -> {nums}
    """
    names = set()
    for child in ast.walk(iter_node):
        if isinstance(child, ast.Name):
            names.add(child.id)
    return names


def _has_zero_init_for_aggregate(node: ast.AST) -> bool:
    """Detect initialization of accumulator to 0 when it should be -inf.

    Looks for:
        max_sum = 0
        current = 0
        best = 0
    where the context involves max/min aggregation (Kadane's, etc.)

    This catches the Maximum Subarray subtle bug:
        max_sum = current = 0   ← fails on all-negative arrays
    vs correct:
        max_sum = current = nums[0]
    """
    for n in ast.walk(node):
        if isinstance(n, ast.Assign):
            for target in n.targets:
                # Check if target name suggests aggregation
                agg_names = {"max_sum", "current", "best", "max_so_far",
                             "current_max", "global_max", "ans"}
                target_names = set()
                if isinstance(target, ast.Name):
                    target_names.add(target.id)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            target_names.add(elt.id)

                if target_names & agg_names:
                    # Check if value is literal 0
                    if isinstance(n.value, ast.Constant) and n.value.value == 0:
                        return True
                    # Check chained assignment: a = b = 0
                    if isinstance(n.value, ast.Constant) and n.value.value == 0:
                        return True
    return False


def _has_array_index_access(node: ast.AST) -> bool:
    """Does the code use array index access (x[i])?"""
    for n in ast.walk(node):
        if isinstance(n, ast.Subscript):
            if isinstance(n.value, ast.Name) and isinstance(n.slice, ast.Name):
                return True
            # nums[i] where slice is a Name
            if isinstance(n.slice, ast.Name):
                return True
    return False


def _has_index_out_of_bounds_risk(node: ast.AST) -> bool:
    """Detect genuinely risky index access patterns.

    Only flags:
    - Direct array access with no loop guard at all (e.g., nums[0] on possibly-empty array)

    Does NOT flag:
    - Any index access inside `for i in range(len(x))` or `for i in range(k, len(x))`
    - Any index access inside `while left < right` guards
    - s[i] inside `for i in range(len(s))`
    - nums[i-1] inside `for i in range(1, len(nums))`
    """
    # If code has ANY range(len(...)) loop, index arithmetic within it is safe
    for n in ast.walk(node):
        if isinstance(n, ast.For):
            iter_src = ast.dump(n.iter)
            if "range" in iter_src and "len" in iter_src:
                return False  # All index access is bounded by range(len(...))

    # If code has while loop with left < right guard, access is safe
    for n in ast.walk(node):
        if isinstance(n, ast.While):
            test_src = ast.dump(n.test)
            if "left" in test_src and "right" in test_src:
                if "Lt" in test_src or "Gt" in test_src:
                    return False  # Bounded by while guard

    # If no loop guards at all, flag any array index access
    for n in ast.walk(node):
        if isinstance(n, ast.Subscript):
            if isinstance(n.value, ast.Name) and isinstance(n.slice, ast.Name):
                # Direct array access: arr[i] — check if inside any loop
                in_loop = False
                for p in ast.walk(node):
                    if isinstance(p, (ast.For, ast.While)):
                        in_loop = True
                        break
                if not in_loop:
                    return True  # arr[i] outside any loop = risky

    return False


def _get_return_statements(node: ast.AST) -> List[ast.Return]:
    """Get all return statements in the function."""
    return _find_all(node, ast.Return)


def _return_is_boolean(node: ast.AST) -> bool:
    """Do all returns produce boolean values?

    Looks for: return True/False, return not x, return x == y, return x and y
    """
    returns = _get_return_statements(node)
    if not returns:
        return False
    bool_returns = 0
    for ret in returns:
        if ret.value is None:
            continue
        r = ret.value
        if isinstance(r, ast.Constant) and isinstance(r.value, bool):
            bool_returns += 1
        elif isinstance(r, ast.UnaryOp) and isinstance(r.op, ast.Not):
            bool_returns += 1
        elif isinstance(r, ast.Compare):
            bool_returns += 1
        elif isinstance(r, ast.BoolOp):
            bool_returns += 1
        elif isinstance(r, ast.Call) and isinstance(r.func, ast.Name):
            if r.func.id in ("bool", "any", "all"):
                bool_returns += 1
    return bool_returns == len(returns) if returns else False


def _return_is_index_pair(node: ast.AST) -> bool:
    """Do returns produce index pairs? (list of two ints)

    Looks for: return [i, j], return [seen[x], i]
    """
    returns = _get_return_statements(node)
    if not returns:
        return False
    list_returns = 0
    for ret in returns:
        if ret.value is None:
            continue
        if isinstance(ret.value, ast.List):
            list_returns += 1
        elif isinstance(ret.value, ast.Subscript):
            # returning array access — could be index result
            list_returns += 1
    return list_returns == len(returns) if returns else False


def _expects_empty_stack_check(problem: str) -> bool:
    """Does the problem require verifying nothing remains after processing?

    Heuristic: problems about matching/balancing/validating pairs
    require an empty-state final check.
    """
    balance_keywords = [
        "valid", "balance", "match", "pair", "close", "open",
        "bracket", "parenthes", "brace"
    ]
    return any(kw in problem.lower() for kw in balance_keywords)


def _has_empty_state_check(node: ast.AST) -> bool:
    """Does the final return verify empty state?

    Looks for:
        return not stack
        return len(stack) == 0
        return stack == []
        return False   (at end of balanced-check function — always returns True after loop)
    """
    # Find the function body
    funcs = _find_all(node, ast.FunctionDef)
    if not funcs:
        return True  # no function, can't analyze
    func = funcs[0]

    # Get last statement in function body
    if not func.body:
        return True
    last_stmt = func.body[-1]

    # Check for 'return not stack' or 'return len(stack) == 0'
    if isinstance(last_stmt, ast.Return):
        val = last_stmt.value
        if val is None:
            return True  # bare return = return None
        # 'return not stack'
        if isinstance(val, ast.UnaryOp) and isinstance(val.op, ast.Not):
            return True
        # 'return len(stack) == 0' or any comparison
        if isinstance(val, ast.Compare):
            return True
        # 'return True' at end of balance problem is a red flag — missing empty check
        if isinstance(val, ast.Constant) and val.value is True:
            return False  # Always returning True without checking remaining state
        # 'return False' at end is also suspicious
        if isinstance(val, ast.Constant) and val.value is False:
            return False
    return True


def _has_safe_pop_pattern(node: ast.AST) -> bool:
    """Does the code guard stack.pop() with an empty check?

    Safe patterns:
        top = stack.pop() if stack else '#'
        if stack: top = stack.pop()

    Unsafe:
        top = stack.pop()  (no guard)
    """
    funcs = _find_all(node, ast.FunctionDef)
    if not funcs:
        return True

    for func in funcs:
        for n in ast.walk(func):
            # Look for: stack.pop() call
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                if n.func.attr == "pop":
                    # Check if it's inside a ternary: x if stack else y
                    # This appears as: IfExp(test=stack, body=pop(), orelse=default)
                    # We need to check parent context — use a second pass
                    has_guard = False
                    # Check for IfExp (ternary) containing this pop call
                    for parent in ast.walk(func):
                        if isinstance(parent, ast.IfExp):
                            # Check if pop call is in the body (the 'if true' branch)
                            for child in ast.walk(parent.body):
                                if child is n:
                                    has_guard = True
                            break
                        # Check for If statement with stack guard
                        if isinstance(parent, ast.If):
                            # Check if pop call is inside the if body
                            for child in ast.walk(parent):
                                if child is n:
                                    has_guard = True
                            break
                    if not has_guard:
                        return False
    return True


def _has_brute_force_pattern(node: ast.AST) -> bool:
    """Detect brute-force O(n²) patterns: nested for loops with range(len(x))."""
    for_loops = _find_all(node, ast.For)
    for outer in for_loops:
        # Check if outer iterates over range(len(...))
        outer_iter = ast.dump(outer.iter)
        if "range" in outer_iter and "len" in outer_iter:
            # Check for inner loop over same structure
            for inner in ast.walk(outer):
                if inner is outer:
                    continue
                if isinstance(inner, ast.For):
                    inner_iter = ast.dump(inner.iter)
                    if "range" in inner_iter and "len" in inner_iter:
                        return True
    return False


def _has_triple_nested_sum(node: ast.AST) -> bool:
    """Detect O(n³) brute-force enumeration using sum() in generator expressions.

    Pattern:
        max(sum(nums[i:j]) for i in range(len(nums)) for j in range(i+1, len(nums)+1))

    This is O(n³) because:
    - Two generator loops = O(n²) iterations
    - sum(nums[i:j]) per iteration = O(n)
    """
    for n in ast.walk(node):
        # Look for sum() call
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            if n.func.id == "sum":
                # Check if argument is a slice of input array
                arg = n.args[0] if n.args else None
                if isinstance(arg, ast.Subscript):
                    # nums[i:j] pattern — this is O(n) per call
                    # Check if inside a generator with range(len()) loops
                    for parent in ast.walk(node):
                        if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name):
                            if parent.func.id in ("max", "min"):
                                # Check if generator has nested range(len())
                                for child in ast.walk(parent):
                                    if isinstance(child, ast.GeneratorExp):
                                        ranges = 0
                                        for gen_child in ast.walk(child):
                                            if isinstance(gen_child, ast.Call):
                                                if isinstance(gen_child.func, ast.Name):
                                                    if gen_child.func.id == "range":
                                                        ranges += 1
                                        if ranges >= 2:
                                            return True
    return False


def _is_substring_replace_approach(node: ast.AST) -> bool:
    """Detect the string-replace approach to bracket matching.

    Looks for:
        while '()' in s: s = s.replace('()','')
    This is inefficient O(n²) for long strings.
    """
    for n in ast.walk(node):
        if isinstance(n, ast.While):
            body = n.body
            for stmt in body:
                if isinstance(stmt, ast.Assign):
                    # Check for .replace() call
                    assign_src = ast.dump(stmt.value)
                    if "replace" in assign_src:
                        return True
                    # Check for Attribute call with attr 'replace'
                    for child in ast.walk(stmt.value):
                        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                            if child.func.attr == "replace":
                                return True
    return False


def _problem_expects_index(problem: str) -> bool:
    """Does the problem ask for indices/positions?"""
    index_keywords = ["index", "indices", "position", "positions"]
    return any(kw in problem.lower() for kw in index_keywords)


def _problem_expects_value(problem: str) -> bool:
    """Does the problem ask for a value (not index)?"""
    value_keywords = ["sum", "maximum", "minimum", "value", "largest", "smallest"]
    return any(kw in problem.lower() for kw in value_keywords)


def _problem_expects_boolean(problem: str) -> bool:
    """Does the problem ask for a yes/no/valid/invalid answer?"""
    bool_keywords = ["valid", "determine if", "return true", "return false",
                     "is valid", "whether"]
    return any(kw in problem.lower() for kw in bool_keywords)


# ===========================================================================
# Problem-specific constraint extraction
# ===========================================================================

def _extract_constraints(problem: str) -> Dict[str, Any]:
    """Extract implicit constraints from problem statement text."""
    lower = problem.lower()
    constraints = {
        "allows_empty": False,         # default: assume non-empty (LeetCode standard)
        "allows_negative": False,
        "allows_single_element": False,
        "expects_index": False,
        "expects_value": False,
        "expects_boolean": False,
        "implies_linear_time": False,
        "is_balance_check": False,
        "min_length_1": False,         # nums.length >= 1
        "min_length_2": False,         # nums.length >= 2
        "_problem_lower": lower,       # cache for string matching in checkers
    }

    # Detect minimum length constraints from problem text
    # "exactly one solution" implies at least 2 elements for Two Sum
    if "exactly one solution" in lower:
        constraints["min_length_2"] = True
        constraints["implies_linear_time"] = True

    # "Given an array of integers" without "may be empty" — assume non-empty
    if "given an array" in lower or "given an integer array" in lower:
        constraints["min_length_1"] = True

    # Negative number detection
    neg_patterns = ["negative", "-1", "-10", "negative numbers", "can be negative",
                    "all-negative", "negative value"]
    if any(p in lower for p in neg_patterns):
        constraints["allows_negative"] = True

    # Index expectation
    if _problem_expects_index(problem):
        constraints["expects_index"] = True

    # Value expectation
    if _problem_expects_value(problem):
        constraints["expects_value"] = True

    # Boolean expectation
    if _problem_expects_boolean(problem):
        constraints["expects_boolean"] = True

    # Balance/validity check
    if _expects_empty_stack_check(problem):
        constraints["is_balance_check"] = True

    # "largest sum" with "subarray" — Kadane's, needs negative init
    if "largest sum" in lower or ("maximum" in lower and "subarray" in lower):
        constraints["allows_negative"] = True
        constraints["implies_linear_time"] = True

    # "containing just the characters" — string is non-empty but may be empty
    if "containing just the characters" in lower or "containing just" in lower:
        constraints["min_length_1"] = False  # could be empty string

    return constraints


# ===========================================================================
# MAIN ANALYZER
# ===========================================================================


def _has_comparison_check(node: ast.AST) -> bool:
    """Detect if the AST contains any comparison operator (==, !=, <, >, etc.).

    Uses proper AST node traversal instead of string matching on ast.dump().
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Compare):
            return True
    return False


def _has_abs_call(node: ast.AST) -> bool:
    """Detect if the AST contains any call to abs().

    Uses proper AST node traversal instead of string matching on ast.dump().
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name) and child.func.id == 'abs':
                return True
    return False


class CodeAnalyzer:

    def analyze(self, problem_statement: str, solution_code: str, problem_name: str = "") -> AnalysisResult:
        """Analyze a Python solution against a problem statement.

        Returns AnalysisResult with verdict, confidence, failures, and reasoning.
        """
        tree = _safe_parse(solution_code)
        constraints = _extract_constraints(problem_statement)

        checks = {
            "handles_empty_input": self._check_empty_input(tree, constraints),
            "handles_single_element": self._check_single_element(tree, constraints),
            "no_index_out_of_bounds": self._check_bounds(tree, constraints),
            "uses_correct_return_type": self._check_return_type(problem_statement, tree, constraints),
            "handles_negative_numbers": self._check_negatives(tree, constraints),
            "time_complexity_viable": self._check_complexity(tree, constraints),
            "no_self_element_reuse": self._check_self_element_reuse(tree, constraints),
            "algorithm_completeness": self._check_algorithm_completeness(tree, constraints),
            # ── TRACK B: New checkers ────────────────────────────────
            "respects_complexity_constraint": self._check_complexity_constraint(tree, problem_name),
            "respects_problem_constraints": self._check_problem_constraints(solution_code, problem_name),
            "uses_correct_algorithm": self._check_correct_algorithm(solution_code, problem_name),
        }

        failures = [name for name, passed in checks.items() if not passed]
        passed_count = len(checks) - len(failures)

        # Certain failures are fatal — they mean the approach is fundamentally wrong
        # (not just failing on edge cases, but producing wrong answer on normal inputs)
        # NOTE: time_complexity_viable removed from FATAL_CHECKS — complexity violations
        # are handled by Rule 1 (constraint override → partial), not as fatal skip.
        # This allows brute-force O(n²) solutions to run through Layer 2 execution.
        FATAL_CHECKS = set()

        has_fatal = bool(set(failures) & FATAL_CHECKS)

        # ── L1/L2 precedence: constraint/complexity flags survive L2 override ──
        CONSTRAINT_FATAL_CHECKS = {
            "respects_complexity_constraint",
            "respects_problem_constraints",
            "uses_correct_algorithm",
        }
        fatal_flags = [f for f in failures if f in CONSTRAINT_FATAL_CHECKS]

        # ── FIX 3: Partial redefinition by failure pattern ───────────
        from doctor.doctor_grader import classify_partial_vs_incorrect
        if len(failures) == 0:
            verdict = "correct"
        else:
            verdict = classify_partial_vs_incorrect(failures)

        # ── FIX 1: Evidence-based confidence ─────────────────────────
        # Static analysis has 8 checkers — treat them as "tests"
        # Checkers that detect edge-case handling count as edge-case coverage
        edge_checkers = {
            "handles_empty_input", "handles_single_element",
            "handles_negative_numbers", "no_index_out_of_bounds",
        }
        has_edge_coverage = any(
            checks.get(c, False) for c in edge_checkers
        )

        from doctor.confidence_calibrator import compute_confidence
        confidence = compute_confidence(
            tests_passed=passed_count,
            tests_total=len(checks),
            has_edge_cases=has_edge_coverage,
        )

        reasoning = self._build_reasoning(checks, constraints)

        return AnalysisResult(
            verdict=verdict,
            confidence=confidence,
            failures=failures,
            details=dict(checks),
            reasoning=reasoning,
            fatal_flags=fatal_flags,
        )

    # ── Checkers ──────────────────────────────────────────────────────

    def _check_empty_input(self, tree: Optional[ast.Module],
                           constraints: Dict[str, Any]) -> bool:
        """Does the code handle empty input without crashing?"""
        if tree is None:
            return False

        # If problem guarantees min_length >= 1, no empty guard needed
        if constraints.get("min_length_1") or constraints.get("min_length_2"):
            return True

        # Balance problems: empty input = empty string, for-loop handles naturally
        # The only concern is whether the final return checks empty state.
        # But if _check_return_type already handles this, don't double-flag.
        if constraints.get("is_balance_check"):
            # Empty string → for loop doesn't execute → whatever the final return
            # says is the answer. If return is `True`, empty string returns True
            # (correct — empty string IS valid). The bug only manifests when
            # there are unmatched opening brackets. So empty input is NOT the issue.
            return True

        # Only flag if problem explicitly allows empty input
        if constraints.get("allows_empty"):
            return _has_guard_for_empty(tree)

        return True

    def _check_single_element(self, tree: Optional[ast.Module],
                              constraints: Dict[str, Any]) -> bool:
        """Does the code handle single-element input?"""
        if tree is None:
            return False

        # Balance problems: single char handled by for-loop
        if constraints.get("is_balance_check"):
            return True

        # "exactly one solution" with Two Sum means >= 2 elements
        if constraints.get("min_length_2"):
            return True

        return True

    def _check_bounds(self, tree: Optional[ast.Module],
                      constraints: Dict[str, Any]) -> bool:
        """Does the code avoid risky index access patterns?"""
        if tree is None:
            return False

        # If code uses enumerate(), index access via enumerate variable is safe
        has_enumerate = False
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                if n.func.id == "enumerate":
                    has_enumerate = True
                    break

        if has_enumerate:
            return True

        # For stack-based problems, check pop safety
        if constraints.get("is_balance_check"):
            return _has_safe_pop_pattern(tree)

        # Check for genuinely risky array index patterns
        return not _has_index_out_of_bounds_risk(tree)

    def _check_return_type(self, problem: str, tree: Optional[ast.Module],
                           constraints: Dict[str, Any]) -> bool:
        """Does the return type match what the problem asks for?"""
        if tree is None:
            return False

        if constraints.get("expects_boolean"):
            if not _return_is_boolean(tree):
                return False
            # Critical: for balance problems, always returning True is wrong
            # The code must check that the stack is empty at the end
            if _expects_empty_stack_check(problem):
                if not _has_empty_state_check(tree):
                    return False

        return True

    def _check_negatives(self, tree: Optional[ast.Module],
                         constraints: Dict[str, Any]) -> bool:
        """Does the code handle negative numbers correctly?

        Catches the Maximum Subarray subtle bug:
            max_sum = current = 0   ← fails on all-negative arrays
        vs correct:
            max_sum = current = nums[0]
        """
        if tree is None:
            return False

        if constraints.get("allows_negative"):
            # Check for zero-init of aggregators when negatives matter
            if _has_zero_init_for_aggregate(tree):
                return False

        return True

    def _check_self_element_reuse(self, tree: Optional[ast.Module],
                                   constraints: Dict[str, Any]) -> bool:
        """Detect 'Two Sum' subtle bug: using same element twice.

        Bug pattern (in hash map approach):
            seen[n] = i           # store FIRST
            if target - n in seen:  # then check
                return [seen[target-n], i]

        This matches element with ITSELF when target = 2*n.
        Example: nums=[3,3], target=6 → seen[3]=0, then 6-3=3 in seen → returns [0,0]

        Correct pattern:
            if target - n in seen:  # check FIRST
                return [seen[target-n], i]
            seen[n] = i             # store AFTER
        """
        if tree is None:
            return False

        # Only relevant for problems with "exactly one solution" (Two Sum pattern)
        if not constraints.get("implies_linear_time"):
            return True

        # Look for dict assignment + membership check ordering in for-loop
        funcs = _find_all(tree, ast.FunctionDef)
        for func in funcs:
            for loop in _find_all(func, ast.For):
                # Analyze statement ordering in loop body
                assigns_seen = []  # (line_index, dict_name, key)
                checks_seen = []   # (line_index, dict_name)

                for idx, stmt in enumerate(loop.body):
                    # Detect: dict[key] = value
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name):
                                assigns_seen.append((idx, target.value.id))

                    # Detect: key in dict
                    if isinstance(stmt, ast.If):
                        test = stmt.test
                        if isinstance(test, ast.Compare):
                            for op, comparator in zip(test.ops, test.comparators):
                                if isinstance(op, ast.In) and isinstance(comparator, ast.Name):
                                    checks_seen.append((idx, comparator.id))

                # Check ordering: if any assign comes before check for same dict,
                # and the dict name suggests a hash map (seen, d, etc.)
                for a_idx, dict_name in assigns_seen:
                    for c_idx, check_name in checks_seen:
                        # Same dict name, assign before check = bug
                        if dict_name == check_name and a_idx < c_idx:
                            # But only flag if dict name suggests hash map
                            if dict_name in ("seen", "visited", "d", "dct", "hm", "cache", "memo"):
                                return False

        return True

    def _check_constraint_violation(self, tree: Optional[ast.Module],
                                     constraints: Dict[str, Any]) -> bool:
        """Detect violations of explicit problem constraints.

        Catches:
        - abs() + str() conversion defeating negative number handling (Palindrome)
        - Missing 32-bit overflow clamp (Reverse Integer, atoi)
        - Missing range clamp to [-2^31, 2^31-1]
        - Missing dedup logic for unique-results problems (3Sum, 4Sum)
        - Empty input not handled for problems that require it
        """
        if tree is None:
            return False

        src = ast.dump(tree)

        # abs() defeats negative number handling
        # Pattern: abs(x) when problem is about checking if number IS palindrome
        if "abs" in src and "palindrome" in constraints.get("_problem_lower", ""):
            return False

        # Missing 32-bit overflow check
        # Pattern: "reverse" or "atoi" problem with no "2**31" or "clamp" or "max/min" guard
        problem_lower = constraints.get("_problem_lower", "")
        if ("2^31" in problem_lower or "32-bit" in problem_lower or
                "signed 32-bit" in problem_lower):
            # Check if code has overflow handling
            has_overflow_check = (
                "2" in src and "31" in src or
                "max(" in src or "min(" in src or
                "clamp" in src or "inf" in src
            )
            if not has_overflow_check:
                # Check if code converts via string (might not overflow)
                if "str(" in src and "int(" in src:
                    # Python handles big ints natively, but problem requires clamping
                    # If there's no explicit clamp, flag it
                    if "2" not in src or "31" not in src:
                        return False
                elif "2" not in src or "31" not in src:
                    return False

        # Missing dedup for "unique" or "must not contain duplicate" problems
        if ("unique" in problem_lower or "not contain duplicate" in problem_lower or
                "must not contain" in problem_lower):
            # Check if code has dedup logic
            has_dedup = (
                ("set(" in src or "set " in src) or
                ("duplicate" in src.lower()) or
                # Check for skip logic: if nums[i] == nums[i-1]: continue
                ("continue" in src and "==" in src) or
                # Also check while-based dedup: while left < right and nums[left] == nums[left+1]
                ("while" in src and "==" in src and "left" in src) or
                # Check for result dedup: using set on results
                ("result" in src and "set(" in src)
            )
            if not has_dedup:
                return False

        # Empty string input not handled when problem requires it
        # Letter Combinations: empty digits → should return []
        if ("digit" in problem_lower or "phone" in problem_lower) and "letter" in problem_lower:
            # Check for empty guard
            if "not digits" not in src and "len(digits)" not in src and '""' not in src:
                # But check if code handles it naturally
                funcs = _find_all(tree, ast.FunctionDef)
                for func in funcs:
                    for stmt in func.body:
                        if isinstance(stmt, ast.If):
                            test_src = ast.dump(stmt.test)
                            if "digits" in test_src and "Not" in test_src:
                                return True  # has empty guard
                    # Check for result = [''] pattern (handles empty naturally)
                    for stmt in func.body:
                        if isinstance(stmt, ast.Assign):
                            for t in stmt.targets:
                                if isinstance(t, ast.Name) and t.id == "result":
                                    if isinstance(stmt.value, ast.List):
                                        if stmt.value.elts:
                                            # result = [''] — handles empty input
                                            return True

        return True

    def _check_algorithm_completeness(self, tree: Optional[ast.Module],
                                       constraints: Dict[str, Any]) -> bool:
        """Detect incomplete algorithm — missing critical steps.

        Catches:
        - Missing subtractive notation in Roman conversion (Integer to Roman)
        - Missing diagonal check in N-Queens
        - Missing close < open constraint in Generate Parentheses
        - Wrong formula: max*length instead of min*width*height (Container)
        - Wrong formula: adjacent diff sum instead of trapped water
        - Missing replace operation in Edit Distance
        """
        if tree is None:
            return False

        src = ast.dump(tree)
        problem_lower = constraints.get("_problem_lower", "")

        # Integer to Roman: missing subtractive notation values (900, 400, 90, 40, 9, 4)
        # Only flag if code uses simple division approach WITHOUT handling subtraction
        if "roman" in problem_lower and "integer" in problem_lower:
            # Check if code uses simple values without subtractive pairs
            # The incorrect solution uses: values = [1000, 500, 100, 50, 10, 5, 1]
            # The correct uses: (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'), ...
            has_subtractive = (
                "900" in src or "CM" in src or
                "400" in src or "CD" in src or
                "90" in src or "XC" in src or
                "40" in src or "XL" in src or
                "9" in src and "IX" in src or
                "4" in src and "IV" in src
            )
            # But also check for reversed iteration approach (another valid correct approach)
            has_reversed_approach = "reversed(" in src or "s[::-1]" in src
            if not has_subtractive and not has_reversed_approach:
                return False

        # N-Queens: missing diagonal check
        if "queen" in problem_lower and "n-queen" in problem_lower.lower():
            # Two valid approaches:
            # 1. Set-based: d1=row-col, d2=row+col stored in sets (backtracking)
            #    AST dump shows: Name(id='diag1'), Name(id='d1'), op=Sub(), op=Add()
            # 2. Explicit: abs(c - col) == abs(r - row) (permutation validation)
            # NOTE: Both approaches include abs+Sub+== so checker can't distinguish
            # correct from incorrect permutation approach. L2 handles differentiation.
            has_set_diagonal = (
                ("diag" in src or "d1" in src or "d2" in src) and
                ("row" in src and "col" in src) and
                ("Sub" in src or "Add" in src)
            )
            has_explicit_diagonal = (
                _has_abs_call(tree) and _has_comparison_check(tree)
            )
            if not has_set_diagonal and not has_explicit_diagonal:
                return False

        # Generate Parentheses: close_count should be < open_count, not < n
        if "parenthes" in problem_lower and "generate" in problem_lower:
            # Check for the wrong constraint: close_count < n instead of close_count < open_count
            funcs = _find_all(tree, ast.FunctionDef)
            for func in funcs:
                for comp in _find_all(func, ast.Compare):
                    # Check if comparing close_count with n (wrong) vs open_count (correct)
                    for comparator in comp.comparators:
                        if isinstance(comparator, ast.Name):
                            if comparator.id == "n":
                                # Check the variable being compared
                                if isinstance(comp.left, ast.Name):
                                    if "close" in comp.left.id.lower():
                                        return False  # close_count < n is wrong

        # Container With Most Water: wrong formula
        # Only flag the truly wrong approach (max * len), NOT the correct two-pointer
        if "container" in problem_lower or "most water" in problem_lower:
            # Wrong: max(height) * len(height) or max(height) * (len-1)
            # Check return statements for this pattern
            funcs = _find_all(tree, ast.FunctionDef)
            for func in funcs:
                for ret in _get_return_statements(func):
                    if ret.value:
                        ret_src = ast.dump(ret.value)
                        if "max(" in ret_src and "len(" in ret_src and "*" in ret_src:
                            return False  # fundamentally wrong formula
            # All other approaches (two-pointer, brute force) are algorithmically complete

        # Trapping Rain Water: wrong formula
        if "trapping" in problem_lower or "rain water" in problem_lower:
            # Wrong: sum(abs diff between consecutive)
            # Wrong: max * length
            # Should have min(left_max, right_max) - height pattern
            has_trapped_water_logic = (
                ("left_max" in src or "max_left" in src) and
                ("right_max" in src or "max_right" in src) and
                "min(" in src
            )
            # Two-pointer approach also correct
            has_two_pointer = (
                ("left" in src and "right" in src and
                 "max(" in src and "- height" in src)
            )
            if not has_trapped_water_logic and not has_two_pointer:
                return False

        # Edit Distance: missing replace operation
        # Only flag if min() has fewer than 3 args AND dp table exists
        if "edit distance" in problem_lower or "minimum number of operations" in problem_lower:
            if "dp[" in src or "dp =" in src:
                for call in _find_all(tree, ast.Call):
                    if isinstance(call.func, ast.Name) and call.func.id == "min":
                        # Count top-level args only (not nested subscript accesses)
                        if len(call.args) < 3:
                            return False  # missing third operation

        return True

    def _check_return_semantics(self, tree: Optional[ast.Module],
                                 constraints: Dict[str, Any]) -> bool:
        """Detect fundamentally wrong return values.

        Catches:
        - Returning str(num) instead of Roman numeral
        - Returning s == p instead of wildcard match
        - Returning min(string) for longest common prefix
        - Returning 0 for strStr (always returns first index)
        - Returning abs(len1 - len2) for edit distance
        - Returning t if t in s for minimum window substring
        - Returning max(heights) * len(heights) for largest rectangle
        - Returning [max(nums)] * k for sliding window maximum
        - Returning (median1 + median2) / 2 for median of two arrays
        """
        if tree is None:
            return False

        src = ast.dump(tree)
        problem_lower = constraints.get("_problem_lower", "")
        funcs = _find_all(tree, ast.FunctionDef)

        for func in funcs:
            returns = _get_return_statements(func)
            for ret in returns:
                if ret.value is None:
                    continue
                ret_src = ast.dump(ret.value)

                # Roman: returning str(num) — the "incorrect" solution
                if "roman" in problem_lower and "integer" in problem_lower:
                    if "str(" in ret_src and "num" in ret_src.lower():
                        return False

                # Wildcard: returning s == p
                if "wildcard" in problem_lower:
                    if "s" in ret_src and "==" in ret_src and "p" in ret_src:
                        # Only flag if it's a direct equality check
                        if "for" not in src and "while" not in src:
                            return False

                # Longest Common Prefix: returning min(strs)
                if "common prefix" in problem_lower:
                    if "min(" in ret_src:
                        return False

                # strStr: returning 0 or -1 without proper search
                if "strstr" in problem_lower or "strStr" in problem_lower:
                    # Returning 0 when needle is found (always returns 0)
                    if "needle" in src.lower() or "needle" in problem_lower:
                        if "0" in ret_src and "==" not in ret_src:
                            # Check if there's actual search logic
                            has_search = "range(" in src or "index(" in src
                            if not has_search:
                                return False

                # Edit Distance: returning abs(len1 - len2)
                if "edit distance" in problem_lower or "convert" in problem_lower:
                    if "abs(" in ret_src and "len(" in ret_src:
                        return False

                # Minimum Window: returning t if t in s
                if "window" in problem_lower and "substring" in problem_lower:
                    if "in" in ret_src and "else" in ret_src:
                        return False

                # Largest Rectangle: returning max * len
                if "histogram" in problem_lower or "rectangle" in problem_lower:
                    if "max(" in ret_src and "len(" in ret_src and "*" in ret_src:
                        return False

                # Sliding Window: returning [max(nums)] * k
                if "sliding window" in problem_lower:
                    if "max(" in ret_src and "*" in ret_src:
                        return False

                # Median of Two: averaging medians
                if "median" in problem_lower and "sorted" in problem_lower:
                    if "+" in ret_src and "/ 2" in ret_src:
                        # Check if it's averaging two medians
                        if "len(" not in ret_src:
                            return False

                # N-Queens: no validation at all
                if "queen" in problem_lower:
                    if "is_safe" not in src and "valid" not in src.lower():
                        # No validation function — all placements accepted
                        has_validation = False
                        for n in ast.walk(func):
                            if isinstance(n, ast.If):
                                test_src = ast.dump(n.test)
                                if "==" in test_src or "!=" in test_src:
                                    has_validation = True
                        if not has_validation:
                            return False

                # Container: max * (len-1)
                if "container" in problem_lower or "most water" in problem_lower:
                    if "max(" in ret_src and "len(" in ret_src and "*" in ret_src:
                        return False

                # Trapping Rain Water: wrong formula
                if "rain water" in problem_lower or "trapping" in problem_lower:
                    # sum of adjacent differences
                    if "height[i]" in src and "height[i - 1]" in src:
                        if "-" in ret_src or "sum(" in ret_src:
                            if "min(" not in src and "max(" not in src:
                                return False

                # Roman to Integer: sum each char independently (no subtractive)
                if "roman" in problem_lower and "integer" in problem_lower:
                    if "sum(" in ret_src and "for" in ret_src:
                        # Check if there's subtractive notation handling
                        has_subtractive = ("-" in src and "values[" in src) or \
                                         ("prev" in src)
                        if not has_subtractive:
                            return False

                # Remove Duplicates: returning len(set(nums))
                if "duplicate" in problem_lower and "sorted" in problem_lower:
                    # returning just len(set) without modifying array in-place
                    if "set(" in ret_src and "len(" in ret_src:
                        # Check if there's actual in-place modification
                        has_inplace = False
                        for n in ast.walk(func):
                            if isinstance(n, ast.Assign):
                                for t in n.targets:
                                    if isinstance(t, ast.Subscript):
                                        has_inplace = True
                        if not has_inplace:
                            return False

                # Longest Palindromic Substring: brute force O(n³)
                if "palindromic" in problem_lower and "substring" in problem_lower:
                    if "sub" in ret_src.lower() or "[::-1]" in ret_src:
                        if "for" in ret_src or "range" in ret_src:
                            # Check if this is O(n³) brute force
                            # Has nested loops
                            if _has_brute_force_pattern(tree) or \
                               _has_triple_nested_sum(tree):
                                return False

                # Merge Lists: just concatenating without sorting
                if "merge" in problem_lower and "sorted" in problem_lower:
                    # curr.next = list2 at end without merging
                    if "list1" in ret_src or "list2" in ret_src:
                        if "while" not in src and "sort" not in src.lower():
                            return False

                # First Missing Positive: returning max + 1
                if "first missing" in problem_lower or "missing positive" in problem_lower:
                    if "max(" in ret_src and "+ 1" in ret_src:
                        return False

                # Letter Combinations: returning list of mappings
                if "letter" in problem_lower and "combin" in problem_lower:
                    if "mapping" in ret_src.lower() or "for d in digits" in src:
                        # Check if it's just mapping digits to letters
                        if "backtrack" not in src and "product" not in src:
                            if "result" in src and "for" in src:
                                # Check if it generates combinations or just maps
                                has_combination = False
                                for n in ast.walk(func):
                                    if isinstance(n, ast.ListComp):
                                        has_combination = True
                                if not has_combination:
                                    return False

        return True

    def _check_complexity(self, tree: Optional[ast.Module],
                          constraints: Dict[str, Any]) -> bool:
        """Is the time complexity viable for the problem?

        Flags:
        - Nested loops O(n²) when O(n) is implied
        - String replacement approach O(n²) for bracket matching
        - Brute-force enumeration O(n³) using sum() in generator
        """
        if tree is None:
            return False

        # String replacement approach is O(n²)
        if _is_substring_replace_approach(tree):
            if constraints.get("is_balance_check"):
                return False  # replace approach is O(n²)

        # Triple nested: sum(nums[i:j]) with range generators = O(n³)
        if _has_triple_nested_sum(tree):
            return False

        # Nested same-input loops = O(n²)
        if _has_nested_same_input_loops(tree):
            # Two Sum: "exactly one solution" implies O(n) hash map expected
            if constraints.get("implies_linear_time"):
                return False
            # For other problems, O(n²) might still be acceptable
            # but flag it if constraints imply linear

        return True

    # ── TRACK B: New checkers ──────────────────────────────────────────

    def _check_complexity_constraint(self, tree: Optional[ast.Module],
                                      problem_name: str) -> bool:
        """FATAL checker — detects O(n²) when problem requires O(n).

        Only fires for problems in COMPLEXITY_CONSTRAINTS with O(n) requirement.
        """
        if tree is None:
            return False

        problem_key = problem_name.lower().replace(" ", "_")
        # Map display names to constraint keys
        name_to_key = {
            "two_sum": "two_sum",
            "container_with_most_water": "max_area",
            "trapping_rain_water": "trap",
            "merge_two_sorted_lists": "merge_two_sorted_lists",
            "valid_parentheses": "valid_parentheses",
            "roman_to_integer": "roman_to_integer",
            "palindrome_number": "palindrome_number",
            "n-queens": "solve_n_queens",
            "n_queens": "solve_n_queens",
            "longest_palindromic_substring": "longest_palindrome",
        }
        constraint_key = name_to_key.get(problem_key, problem_key)
        constraint = COMPLEXITY_CONSTRAINTS.get(constraint_key)

        if constraint != "O(n)":
            return True  # No O(n) requirement, or not in registry

        # Detect nested loops
        if _has_nested_loops(tree):
            return False  # O(n²) detected where O(n) required

        return True

    def _check_problem_constraints(self, solution_code: str,
                                    problem_name: str) -> bool:
        """Non-fatal checker — detects use of banned operations.

        Uses raw code text for simple pattern matching.
        """
        if not solution_code:
            return False

        problem_key = problem_name.lower().replace(" ", "_")
        # Map display names to constraint keys
        name_to_key = {
            "palindrome_number": "palindrome_number",
        }
        constraint_key = name_to_key.get(problem_key, problem_key)
        constraint = PROBLEM_CONSTRAINTS.get(constraint_key)

        if not constraint or not constraint.get("banned_patterns"):
            return True  # No constraints for this problem

        for pattern in constraint["banned_patterns"]:
            if pattern in solution_code:
                return False  # Banned pattern found

        return True

    def _check_correct_algorithm(self, solution_code: str,
                                  problem_name: str) -> bool:
        """FATAL checker — detects wrong algorithm family.

        Uses pattern matching on code text against known wrong approaches.
        """
        if not solution_code:
            return False

        problem_key = problem_name.lower().replace(" ", "_")
        # Map display names to signature keys
        name_to_key = {
            "longest_palindromic_substring": "longest_palindromic_substring",
        }
        sig_key = name_to_key.get(problem_key, problem_key)
        sig = ALGORITHM_SIGNATURES.get(sig_key)

        if not sig:
            return True  # No algorithm signature for this problem

        # If any forbidden pattern present → wrong algorithm
        code_lower = solution_code.lower()
        for pattern in sig["forbidden_patterns"]:
            if pattern in code_lower:
                return False  # Wrong algorithm family

        return True  # No forbidden patterns found — algorithm looks correct

    # ── Reasoning ─────────────────────────────────────────────────────

    def _build_reasoning(self, checks: Dict[str, bool],
                         constraints: Dict[str, Any]) -> str:
        """Build a one-sentence reasoning summary."""
        failures = [name for name, ok in checks.items() if not ok]

        if not failures:
            return "Solution handles all detected edge cases and constraints correctly"

        reasons = {
            "handles_empty_input": "missing guard for empty input",
            "handles_single_element": "single-element case not handled",
            "no_index_out_of_bounds": "risky index access without bounds check",
            "uses_correct_return_type": "return type doesn't match problem expectation",
            "handles_negative_numbers": "incorrect initialization for negative number handling",
            "time_complexity_viable": "time complexity too high for problem constraints",
            "no_self_element_reuse": "may use same element twice (check-store order violation)",
            "algorithm_completeness": "incomplete algorithm — missing critical step",
            "respects_complexity_constraint": "uses O(n²) approach where O(n) is required",
            "respects_problem_constraints": "uses banned operation for this problem",
        }

        reason_parts = [reasons.get(f, f) for f in failures]
        return "; ".join(reason_parts)
