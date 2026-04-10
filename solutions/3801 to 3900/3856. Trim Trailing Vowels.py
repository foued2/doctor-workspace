"""
LeetCode 3856. Trim Trailing Vowels
============================================================

Problem Number: 3856
Difficulty Rating: 1139.53 (ZeroTrac)
Contest: weekly-contest-491
Problem Index: Q1

LeetCode URL: https://leetcode.com/problems/trim-trailing-vowels/

Problem Slug: trim-trailing-vowels
Chinese Title: 移除尾部元音字母

PROBLEM STATEMENT:
============================================================
You are given a string `s` that consists of lowercase English letters.

Return the string obtained by removing **all** trailing **vowels** from `s`.

The **vowels** consist of the characters `'a'`, `'e'`, `'i'`, `'o'`, and `'u'`.

 

Example 1:**

**Input:** s = "idea"

**Output:** "id"

**Explanation:**

Removing `"id**ea**"`, we obtain the string `"id"`.

Example 2:**

**Input:** s = "day"

**Output:** "day"

**Explanation:**

There are no trailing vowels in the string `"day"`.

Example 3:**

**Input:** s = "aeiou"

**Output:** ""

**Explanation:**

Removing `"**aeiou**"`, we obtain the string `""`.

 

**Constraints:**

	
• `1 <= s.length <= 100`
	
• `s` consists of only lowercase English letters.

DIFFICULTY: Easy
LIKES: 34 | DISLIKES: 0
TOPICS: String


============================================================
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
============================================================
TODO #1 — PROBLEM STATEMENT      [Review auto-generated content above ✅]
TODO #2 — APPROACH                [Describe your algorithm step-by-step]
TODO #3 — COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 — SOLUTION + TESTS        [Implement solution + comprehensive test cases]
============================================================

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py 3856`
          Must pass in order: #1 → #2 → #3 → #4
          Each requires ≥8/10 to pass (except #4 needs 100% test pass)

============================================================
TODO #2 — APPROACH:
TODO: Replace this line with your algorithm description.
      Explain step-by-step how you will solve this problem.
      Example: "I will use a hash map to store..." or "This is a sliding window problem where..."

============================================================
TODO #3 — COMPLEXITY:
Time Complexity: O(?)  — replace with actual complexity (e.g., O(n log n))
Space Complexity: O(?) — replace with actual complexity (e.g., O(n) for hash map)
"""

from typing import List, Optional
import heapq
from collections import defaultdict, deque


class Solution:
    @staticmethod
    def solve() -> None:
        """
        TODO #4a — Implement the solution for Trim Trailing Vowels

        Args:
            TODO: Add parameters based on the problem statement

        Returns:
            TODO: Add return type based on the problem statement
        """
        # TODO: Implement your solution here
        pass


# ============================================================
# TODO #4b — Test Cases (add from LeetCode examples + edge cases)
# ============================================================
def _run_embedded_tests() -> None:
    solution = Solution()

    # Example 1:
    # Input: TODO
    # Expected: TODO

    # Example 2:
    # Input: TODO
    # Expected: TODO

    # Edge case:
    # Input: TODO
    # Expected: TODO

    result = solution.solve()
    print(f"Result: {result}")


if __name__ == '__main__':
    from pathlib import Path
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from doctor_runtime import run_doctor_or_embedded_tests

    raise SystemExit(run_doctor_or_embedded_tests(__file__, _run_embedded_tests))
