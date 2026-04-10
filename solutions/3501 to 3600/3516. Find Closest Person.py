"""
LeetCode 3516. Find Closest Person
============================================================

Problem Number: 3516
Difficulty Rating: 1164.15 (ZeroTrac)
Contest: weekly-contest-445
Problem Index: Q1

LeetCode URL: https://leetcode.com/problems/find-closest-person/

Problem Slug: find-closest-person
Chinese Title: 找到最近的人

PROBLEM STATEMENT:
============================================================
You are given three integers x`, y`, and z`, representing the positions of three people on a number line:

	x` is the position of Person 1.
	y` is the position of Person 2.
	z` is the position of Person 3, who does **not** move.

Both Person 1 and Person 2 move toward Person 3 at the **same** speed.

Determine which person reaches Person 3 **first**:

	Return 1 if Person 1 arrives first.
	Return 2 if Person 2 arrives first.
	Return 0 if both arrive at the **same** time.

Return the result accordingly.

 

Example 1:**

**Input:** x = 2, y = 7, z = 4

**Output:** 1

**Explanation:**

	Person 1 is at position 2 and can reach Person 3 (at position 4) in 2 steps.
	Person 2 is at position 7 and can reach Person 3 in 3 steps.

Since Person 1 reaches Person 3 first, the output is 1.

Example 2:**

**Input:** x = 2, y = 5, z = 6

**Output:** 2

**Explanation:**

	Person 1 is at position 2 and can reach Person 3 (at position 6) in 4 steps.
	Person 2 is at position 5 and can reach Person 3 in 1 step.

Since Person 2 reaches Person 3 first, the output is 2.

Example 3:**

**Input:** x = 1, y = 5, z = 3

**Output:** 0

**Explanation:**

	Person 1 is at position 1 and can reach Person 3 (at position 3) in 2 steps.
	Person 2 is at position 5 and can reach Person 3 in 2 steps.

Since both Person 1 and Person 2 reach Person 3 at the same time, the output is 0.

 

**Constraints:**

	
• `1 <= x, y, z <= 100`

DIFFICULTY: Easy
LIKES: 426 | DISLIKES: 47
TOPICS: Math


============================================================
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
============================================================
TODO #1 - PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 - APPROACH                [Describe your algorithm step-by-step]
TODO #3 - COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 - SOLUTION + TESTS        [Implement solution + comprehensive test cases]
============================================================

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py 3516`
          Must pass in order: #1 -> #2 -> #3 -> #4
          Each requires >=8/10 to pass (except #4 needs 100% test pass)

============================================================
TODO #2 - APPROACH:
This is a simple math/distance problem. Given three positions x, y, z on a
number line, we need to determine which of Person 1 (at x) or Person 2 (at y)
reaches Person 3 (at z) first. Both Person 1 and Person 2 move toward z at
the same speed.

Algorithm:
1. Calculate the distance from Person 1 to Person 3: dist1 = abs(x - z)
2. Calculate the distance from Person 2 to Person 3: dist2 = abs(y - z)
3. Compare distances:
   - If dist1 < dist2: Person 1 arrives first, return 1
   - If dist2 < dist1: Person 2 arrives first, return 2
   - If dist1 == dist2: Both arrive at the same time, return 0

This works because both people move at the same speed, so whoever has the
shorter distance arrives first. Equal distances mean equal arrival times.

============================================================
TODO #3 - COMPLEXITY:
Time Complexity: O(1) — only basic arithmetic operations (subtraction, absolute value, comparison)
Space Complexity: O(1) — no additional data structures; only a few scalar variables
"""

from typing import List, Optional
import heapq
from collections import defaultdict, deque


class Solution:
    @staticmethod
    def solve(x: int, y: int, z: int) -> int:
        """
        Determine which person reaches Person 3 first.

        Args:
            x: position of Person 1
            y: position of Person 2
            z: position of Person 3 (stationary)

        Returns:
            1 if Person 1 arrives first,
            2 if Person 2 arrives first,
            0 if both arrive at the same time
        """
        dist1 = abs(x - z)
        dist2 = abs(y - z)
        if dist1 < dist2:
            return 1
        elif dist2 < dist1:
            return 2
        else:
            return 0


# ============================================================
# TODO #4b — Test Cases (add from LeetCode examples + edge cases)
# ============================================================
def _run_embedded_tests() -> None:
    solution = Solution()
    passed = 0
    failed = 0

    def check(x, y, z, expected, label=""):
        nonlocal passed, failed
        result = solution.solve(x, y, z)
        if result == expected:
            passed += 1
            print(f"  PASS: {label} -> solve({x}, {y}, {z}) = {result}")
        else:
            failed += 1
            print(f"  FAIL: {label} -> solve({x}, {y}, {z}) = {result}, expected {expected}")

    # Example 1: Person 1 is closer
    check(2, 7, 4, 1, "Example 1: x=2, y=7, z=4 -> Person 1 closer")

    # Example 2: Person 2 is closer
    check(2, 5, 6, 2, "Example 2: x=2, y=5, z=6 -> Person 2 closer")

    # Example 3: Equal distance
    check(1, 5, 3, 0, "Example 3: x=1, y=5, z=3 -> Equal distance")

    # Edge case: Person 1 at same position as Person 3
    check(4, 10, 4, 1, "Edge: Person 1 already at z")

    # Edge case: Person 2 at same position as Person 3
    check(1, 4, 4, 2, "Edge: Person 2 already at z")

    # Edge case: All at same position
    check(5, 5, 5, 0, "Edge: All at same position")

    # Edge case: Large values (constraint boundary)
    check(1, 100, 50, 1, "Boundary: x=1, y=100, z=50")
    check(100, 1, 50, 2, "Boundary: x=100(dist=50), y=1(dist=49) -> Person 2 closer")

    # Edge case: Negative relative positions (all positive per constraint)
    check(10, 20, 15, 0, "Midpoint: x=10(dist=5), y=20(dist=5) -> equal")

    print(f"\nResults: {passed} passed, {failed} failed out of {passed + failed} tests")
    if failed > 0:
        raise AssertionError(f"{failed} test(s) failed")
    print("All tests passed!")


if __name__ == '__main__':
    from pathlib import Path
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from doctor_runtime import run_doctor_or_embedded_tests

    raise SystemExit(run_doctor_or_embedded_tests(__file__, _run_embedded_tests))
