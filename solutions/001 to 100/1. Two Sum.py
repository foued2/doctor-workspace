"""
LeetCode 1. Two Sum
============================================================

Problem Number: 1
Difficulty Rating: Easy
Contest: N/A
Problem Index: Q1

LeetCode URL: https://leetcode.com/problems/two-sum/

Problem Slug: two-sum
Chinese Title: 两数之和

PROBLEM STATEMENT:
============================================================
Given an array of integers `nums` and an integer `target`,
return indices of the two numbers such that they add up to `target`.

You may assume that each input would have **exactly one solution**,
and you may not use the same element twice.

You can return the answer in any order.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Example 2:
Input: nums = [3,2,4], target = 6
Output: [1,2]

Example 3:
Input: nums = [3,3], target = 6
Output: [0,1]

Constraints:
• `2 <= nums.length <= 10^4`
• `-10^9 <= nums[i] <= 10^9`
• `-10^9 <= target <= 10^9`
• **Only one valid answer exists.**

DIFFICULTY: Easy
TOPICS: Array, Hash Table


============================================================
TODO WORKFLOW - Complete in Order (1 -> 2 -> 3 -> 4):
============================================================
TODO #1 - PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 - APPROACH                [Describe your algorithm step-by-step]
TODO #3 - COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 - SOLUTION + TESTS        [Implement solution + comprehensive test cases]
============================================================

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py 1`
          Must pass in order: #1 -> #2 -> #3 -> #4
          Each requires >=8/10 to pass (except #4 needs 100% test pass)

============================================================
TODO #2 - APPROACH:
I will use a hash map (dictionary) to store numbers we have already seen,
mapping each number to its index. As I iterate through the array, I will
compute the complement (target - current_num) and check if it is already
in the hash map. If found, return both indices. If not, store the
current number and continue.

Algorithm:
1. Initialize an empty dict: num_dict = {}
2. Loop through nums with index i and value num
3. Compute complement = target - num
4. If complement in num_dict, return [num_dict[complement], i]
5. Otherwise, store num_dict[num] = i
6. Return None if no pair found (should not happen per constraints)

============================================================
TODO #3 - COMPLEXITY:
Time Complexity: O(n) — single pass through array, dict lookups are O(1) average
Space Complexity: O(n) — hash map stores up to n elements in worst case
"""

from typing import List


class Solution:
    @staticmethod
    def twoSum(nums: List[int], target: int) -> List[int]:
        """
        Find indices of two numbers that add up to target.

        Args:
            nums: List of integers
            target: Target sum

        Returns:
            List of two indices whose values sum to target
        """
        num_dict = {}

        for i, num in enumerate(nums):
            complement = target - num
            if complement in num_dict:
                return [num_dict[complement], i]
            num_dict[num] = i

        return []  # Should never reach here per problem constraints


# ============================================================
# TODO #4b — Test Cases (add from LeetCode examples + edge cases)
# ============================================================
def _run_embedded_tests() -> None:
    solution = Solution()

    # Example 1: nums = [2,7,11,15], target = 9, output = [0,1]
    result = solution.twoSum([2, 7, 11, 15], 9)
    print(f"[2,7,11,15], target=9 -> {result}")
    assert sorted(result) == [0, 1], f"Expected [0,1], got {result}"

    result = solution.twoSum([3, 2, 4], 6)
    print(f"[3,2,4], target=6 -> {result}")
    assert sorted(result) == [1, 2], f"Expected [1,2], got {result}"

    result = solution.twoSum([3, 3], 6)
    print(f"[3,3], target=6 -> {result}")
    assert sorted(result) == [0, 1], f"Expected [0,1], got {result}"

    result = solution.twoSum([-10**9, 10**9], 0)
    print(f"[-1e9, 1e9], target=0 -> {result}")
    assert sorted(result) == [0, 1], f"Expected [0,1], got {result}"

    result = solution.twoSum([-1, -2, -3, -4], -6)
    print(f"[-1,-2,-3,-4], target=-6 -> {result}")
    assert sorted(result) == [1, 3], f"Expected [1,3], got {result}"

    print("\n[ALL TESTS PASSED]")


if __name__ == '__main__':
    from pathlib import Path
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from doctor_runtime import run_doctor_or_embedded_tests

    raise SystemExit(run_doctor_or_embedded_tests(__file__, _run_embedded_tests))
