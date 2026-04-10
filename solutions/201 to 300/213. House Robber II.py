from typing import List


class Solution:
    @staticmethod
    def rob(nums: List[int]) -> int:
        # Check if the list of houses is empty
        if not nums:
            return 0

        # Simplify the length of nums to avoid redundancy and manipulate it
        n = len(nums)

        # If there's only one house, return the money from that house
        if n == 1:
            return nums[0]

        # If there are only two houses, return the maximum money that can be robbed from either house
        if n == 2:
            return max(nums)

        # Initialize an array to store the maximum money that can be robbed up to each house
        dp = [0 for _ in range(n)]

        # Create one model function of the core solution
        def house(n_nums):
            # Initialize the first two elements of dp array with the money from the first and second houses respectively
            dp[0], dp[1] = nums[0], max(n_nums[0], n_nums[1])

            # Iterate over the remaining houses starting from the third house
            for i in range(2, n - 1):
                # Calculate the maximum money that can be robbed up to the current house
                dp[i] = max(dp[i - 2] + n_nums[i], dp[i - 1])

            # Return the maximum money that can be robbed up to the last house
            return dp[n - 2]

        # Set the two ranges of nums to permeate between them
        nums1 = nums[:n - 1]
        nums2 = nums[1: n]

        # Return the maximum solution of the two operations
        return max(house(nums1), house(nums2))


# Test the rob function with the provided examples
print(Solution.rob(nums=[2, 3, 2]))  # Expected output: 3
print(Solution.rob(nums=[1, 2, 3, 1]))  # Expected output: 4
print(Solution.rob(nums=[1, 2, 3]))  # Expected output: 3
