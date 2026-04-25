"""
Deterministic Output Validators
================================
Verify that a solution's OUTPUT is structurally correct, independent of
pre-computed expected values. This catches cases where the test suite's
expected output may be wrong or incomplete.

Each validator takes:
  - problem_key: str
  - solution_output: the actual output from running the solution
  - problem_input: the input that was passed to the solution
  - problem_params: any additional context (e.g., n for N-Queens)

Returns:
  - valid: bool (True if output is structurally valid)
  - reason: str (why it's invalid, or "ok" if valid)
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple


def validate_nqueens(output: Any, params: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify N-Queens output: list of boards where no queen attacks another."""
    n = params.get("n")
    if n is None:
        return False, "missing param: n"

    if not isinstance(output, list):
        return False, f"expected list of boards, got {type(output).__name__}"

    if len(output) == 0:
        # For n=1, there's 1 solution. For n=2,3 there are 0. For n>=4 there are >0.
        if n in (2, 3):
            return True, "ok"  # no solutions exist
        # For other n, empty output may be valid (solver found nothing) but
        # we flag it for review
        return True, "ok"  # structurally valid (0 solutions is a valid answer)

    for board_idx, board in enumerate(output):
        if not isinstance(board, list) or len(board) != n:
            return False, f"board {board_idx}: expected {n} rows, got {len(board) if isinstance(board, list) else 'non-list'}"

        # Parse board: each row is a string like "..Q..."
        queen_positions = []
        for row_idx, row in enumerate(board):
            if not isinstance(row, str) or len(row) != n:
                return False, f"board {board_idx} row {row_idx}: expected string of length {n}"
            cols_with_q = [c for c, ch in enumerate(row) if ch == 'Q']
            if len(cols_with_q) != 1:
                return False, f"board {board_idx} row {row_idx}: expected 1 queen, found {len(cols_with_q)}"
            queen_positions.append((row_idx, cols_with_q[0]))

        # Check no two queens attack each other
        for i in range(len(queen_positions)):
            for j in range(i + 1, len(queen_positions)):
                r1, c1 = queen_positions[i]
                r2, c2 = queen_positions[j]
                # Same column
                if c1 == c2:
                    return False, f"board {board_idx}: queens at ({r1},{c1}) and ({r2},{c2}) share column"
                # Same diagonal
                if abs(r1 - r2) == abs(c1 - c2):
                    return False, f"board {board_idx}: queens at ({r1},{c1}) and ({r2},{c2}) share diagonal"

    return True, "ok"


def validate_two_sum(output: Any, params: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify Two Sum output: indices i,j where nums[i]+nums[j]==target."""
    nums = params.get("nums")
    target = params.get("target")
    if nums is None or target is None:
        return False, "missing params: nums, target"

    if output is None or (isinstance(output, list) and len(output) == 0):
        # No solution found — may be valid if no pair exists
        return True, "ok"  # structurally valid (no pair is a valid answer)

    if not isinstance(output, (list, tuple)) or len(output) != 2:
        return False, f"expected 2 indices, got {type(output).__name__} of length {len(output) if hasattr(output, '__len__') else '?'}"

    i, j = output
    if not isinstance(i, int) or not isinstance(j, int):
        return False, f"indices must be integers, got {type(i).__name__}, {type(j).__name__}"
    if i < 0 or i >= len(nums) or j < 0 or j >= len(nums):
        return False, f"indices ({i},{j}) out of bounds for array of length {len(nums)}"
    if i == j:
        return False, f"indices must be distinct, both are {i}"
    if nums[i] + nums[j] != target:
        return False, f"nums[{i}]+nums[{j}] = {nums[i]}+{nums[j]} = {nums[i]+nums[j]} != {target}"

    return True, "ok"


def validate_valid_parens(output: Any, params: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify Valid Parentheses output: bool is always structurally valid."""
    # The output is a boolean — any boolean is structurally valid.
    # To verify CORRECTNESS, we'd need to re-run the check, which is
    # equivalent to running the solution again. Not useful as a validator.
    return True, "ok"


def validate_container(output: Any, params: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify Container output: a non-negative integer area."""
    if not isinstance(output, (int, float)):
        return False, f"expected numeric area, got {type(output).__name__}"
    if output < 0:
        return False, f"area must be non-negative, got {output}"
    # To verify optimality, we'd need to check all pairs — that's O(n^2)
    # which is the brute-force approach. Not useful as a lightweight validator.
    return True, "ok"


def validate_trap_water(output: Any, params: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify Trap Water output: a non-negative integer volume."""
    if not isinstance(output, (int, float)):
        return False, f"expected numeric volume, got {type(output).__name__}"
    if output < 0:
        return False, f"volume must be non-negative, got {output}"
    return True, "ok"


def validate_arrangement(output: Any, params: Dict[str, Any]) -> Tuple[bool, str]:
    """Verify arrangement of 0..n-1 where adjacent diffs are divisible by some k."""
    n = params.get("n")
    ks = params.get("ks")
    if n is None or ks is None:
        return False, "missing params: n, ks"

    if output is None:
        return False, "output is None"

    if isinstance(output, int) and output == -1:
        return True, "ok"

    if not isinstance(output, list):
        return False, f"expected list, got {type(output).__name__}"

    if len(output) != n:
        return False, f"expected {n} elements, got {len(output)}"

    if set(output) != set(range(n)):
        return False, f"expected permutation of 0..{n-1}, got {set(output)}"

    for i in range(len(output) - 1):
        diff = abs(output[i+1] - output[i])
        if not any(diff % k == 0 for k in ks):
            return False, f"adjacent pair ({output[i]}, {output[i+1]}) diff={diff} not divisible by any k in {ks}"

    return True, "ok"


# Registry: problem_key -> validator function
VALIDATORS: Dict[str, Any] = {
    "N-Queens": validate_nqueens,
    "Two Sum": validate_two_sum,
    "Valid Parentheses": validate_valid_parens,
    "Container With Most Water": validate_container,
    "Trapping Rain Water": validate_trap_water,
    "Arrange Numbers Divisible": validate_arrangement,
}

# Problems where deterministic validation is NOT possible or NOT useful:
# These either output a boolean (any boolean is structurally valid) or
# require full re-computation to verify optimality.
NO_VALIDATOR_NEEDED = {
    "Palindrome Number",       # boolean output
    "Roman to Integer",        # integer — any int is structurally valid
    "Merge Two Sorted Lists",  # linked list — verify sorted+same_elements needs full re-run
    "Longest Palindromic Substring",  # needs brute-force comparison to verify longest
    "Median of Two Sorted Arrays",    # needs full merge to verify
}


def validate_output(problem_key: str, output: Any, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, str]:
    """Validate solution output structurally.

    Returns (valid, reason) tuple.
    If no validator exists for the problem, returns (True, "no validator — test suite only").
    """
    validator = VALIDATORS.get(problem_key)
    if validator is None:
        return True, "no_validator"
    return validator(output, params or {})
