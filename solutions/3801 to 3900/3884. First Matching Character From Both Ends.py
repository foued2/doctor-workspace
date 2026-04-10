"""
LeetCode 3884. First Matching Character From Both Ends
============================================================

Problem Number: 3884
Difficulty Rating: 1161.11 (ZeroTrac)
Contest: weekly-contest-495
Problem Index: Q1

LeetCode URL: https://leetcode.com/problems/first-matching-character-from-both-ends/

Problem Slug: first-matching-character-from-both-ends
Chinese Title: 双端字符匹配

PROBLEM STATEMENT:
============================================================
You are given a string `s` of length `n` consisting of lowercase English letters.

Return the smallest index `i` such that `s[i] == s[n - i - 1]`.

If no such index exists, return -1.

 

Example 1:**

**Input:** s = "abcacbd"

**Output:** 1

**Explanation:**

At index `i = 1`, `s[1]` and `s[5]` are both `'b'`.

No smaller index satisfies the condition, so the answer is 1.

Example 2:**

**Input:** s = "abc"

**Output:** 1

**Explanation:**

​​​​​​​At index `i = 1`, the two compared positions coincide, so both characters are `'b'`.

No smaller index satisfies the condition, so the answer is 1.

Example 3:**

**Input:** s = "abcdab"

**Output:** -1

**Explanation:**

​​​​​​​For every index `i`, the characters at positions `i` and `n - i - 1` are different.

Therefore, no valid index exists, so the answer is -1.

 

**Constraints:**

	
• `1 <= n == s.length <= 100`
	
• `s` consists of lowercase English letters.

DIFFICULTY: Easy
LIKES: 27 | DISLIKES: 0
TOPICS: None


============================================================
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
============================================================
TODO #1 - PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 - APPROACH                [Describe your algorithm step-by-step]
TODO #3 - COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 - SOLUTION + TESTS        [Implement solution + comprehensive test cases]
============================================================

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py 3884`
          Must pass in order: #1 -> #2 -> #3 -> #4
          Each requires >=8/10 to pass (except #4 needs 100% test pass)

============================================================
TODO #2 - APPROACH:
TODO: Replace this line with your algorithm description.
      Explain step-by-step how you will solve this problem.
      Example: "I will use a hash map to store..." or "This is a sliding window problem where..."

============================================================
TODO #3 - COMPLEXITY:
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
        TODO #4a — Implement the solution for First Matching Character From Both Ends

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
