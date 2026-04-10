from bisect import bisect_left, bisect_right
from typing import List


class Solution:
    @staticmethod
    def isMajorityElement(nums: List[int], target: int) -> bool:
        """
        Determine if the target element is a majority element in the sorted list nums.
        """
        def is_majority(candidate):
            """
            Check if the candidate is the majority element in nums.
            """
            # Use bisect_left to find the leftmost index where the candidate appears
            left = bisect_left(nums, candidate)
            # Use bisect_right to find the rightmost index where the candidate appears
            right = bisect_right(nums, candidate)
            # Check if the count of the candidate is greater than half the length of nums
            return (right - left) > len(nums) // 2

        # Check if the target is the majority element in the array
        return is_majority(target)


# Test the function
print(Solution.isMajorityElement(nums=[10, 100, 101, 101], target=101))
