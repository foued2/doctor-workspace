"""
LeetCode 1002. Find Common Characters
============================================================

Problem Number: 1002
Difficulty Rating: 1279.77 (ZeroTrac)
Contest: weekly-contest-126
Problem Index: Q1

LeetCode URL: https://leetcode.com/problems/find-common-characters/

Problem Slug: find-common-characters
Chinese Title: 查找常用字符

PROBLEM STATEMENT:
============================================================
Given a string array `words`, return *an array of all characters that show up in all strings within the *`words`* (including duplicates)*. You may return the answer in **any order**.

 

Example 1:**

```
**Input:** words = ["bella","label","roller"]
**Output:** ["e","l","l"]

```
Example 2:**

```
**Input:** words = ["cool","lock","cook"]
**Output:** ["c","o"]

```

 

**Constraints:**

	
• `1 <= words.length <= 100`
	
• `1 <= words[i].length <= 100`
	
• `words[i]` consists of lowercase English letters.

DIFFICULTY: Easy
LIKES: 4519 | DISLIKES: 439
TOPICS: Array, Hash Table, String


============================================================
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
============================================================
TODO #1 - PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 - APPROACH                [Describe your algorithm step-by-step]
TODO #3 - COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 - SOLUTION + TESTS        [Implement solution + comprehensive test cases]
============================================================

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py 1002`
          Must pass in order: #1 -> #2 -> #3 -> #4
          Each requires >=8/10 to pass (except #4 needs 100% test pass)

============================================================
TODO #2 - APPROACH:
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
        TODO #4a — Implement the solution for Find Common Characters

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
