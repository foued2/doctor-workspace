from typing import List


class Solution:
    @staticmethod
    def findFinalValue(nums: List[int], original: int) -> int:
        # Initialize ori with the value of original
        ori = original

        # Start an infinite loop
        while True:
            # Check if ori is in the list nums
            if ori in nums:
                # If ori is found in nums, double its value
                ori *= 2
            else:
                # If ori is not found in nums, return the current value of ori
                return ori


print(Solution.findFinalValue(nums=[2, 7, 9], original=4))
