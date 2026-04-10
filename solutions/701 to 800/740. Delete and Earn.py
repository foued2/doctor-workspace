from typing import List
from collections import Counter


class Solution:
    @staticmethod
    def deleteAndEarn(nums: List[int]) -> int:
        """
        Hash Table, Dynamic Programming
        """
        # Find the maximum element in the nums list
        max_num = max(nums)

        # Initialize an array to store the sum of values corresponding to each unique number
        sums = [0] * (max_num + 1)

        # Populate the sums array by summing up the values corresponding to each unique number
        for num in nums:
            sums[num] += num

        # Initialize a DP array to store the maximum points considering each unique number as the last number chosen
        dp = [0] * (max_num + 1)

        # Base cases for DP
        dp[0] = 0  # No points if the list is empty
        dp[1] = sums[1]  # Points earned if the list contains only the number 1

        # Iterate through each unique number starting from 2
        for i in range(2, max_num + 1):
            # Calculate the maximum points if we choose the current number
            take = sums[i] + dp[i - 2]

            # Calculate the maximum points if we skip the current number
            skip = dp[i - 1]

            # Update the DP array with the maximum of taking or skipping the current number
            dp[i] = max(take, skip)

        # Return the maximum points obtained considering all unique numbers
        return dp[max_num]

    # Example usage:
    nums = [3, 4, 2]
    print(deleteAndEarn(nums))  # Output: 6
