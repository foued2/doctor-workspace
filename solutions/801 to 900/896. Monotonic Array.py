from typing import List


class Solution:
    @staticmethod
    def isMonotonic(nums: List[int]) -> bool:
        # Get the length of the nums list
        n = len(nums)

        # If the list has 2 or fewer elements, it is monotonic by definition
        if n <= 2:
            return True

        # Iterate through the list starting from the second element
        for i in range(1, n):
            # If the current element is greater than the previous one
            if nums[i] > nums[i - 1]:
                # Check for any violation of the increasing condition
                for j in range(i, n - 1):
                    if nums[j + 1] < nums[j]:
                        return False
                return True

            # If the current element is smaller than the previous one
            if nums[i] < nums[i - 1]:
                # Check for any violation of the decreasing condition
                for j in range(i, n - 1):
                    if nums[j + 1] > nums[j]:
                        return False
                return True

        # If all elements are the same, the list is monotonic
        return True


print(Solution.isMonotonic(
    nums=[-99996, -99991, -99991, -99987, -99984, -99983, -99982, -99981, -99980, -99979, -99975, -99973, -99971,
          -99966, -99962, -99959]))
