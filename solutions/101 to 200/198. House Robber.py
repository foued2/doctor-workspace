from typing import List


class Solution:
    @staticmethod
    def rob(nums: List[int]) -> int:
        """
        Dynamic programming
        """
        # Check if the list of houses is empty
        if not nums:
            return 0

        # Get the length of the list of houses
        n = len(nums)

        # If there's only one house, return the money from that house
        if n == 1:
            return nums[0]

        # Initialize variables to track the maximum money robbed up to the current house
        # prev_robbed: maximum money robbed up to the previous house
        # prev_not_robbed: maximum money robbed up to the previous house without robbing it
        prev_robbed = nums[0]
        prev_not_robbed = 0

        # Iterate through the houses starting from the second one
        for i in range(1, n - 1):
            # Calculate the maximum money that can be robbed up to the current house If we rob the current house,
            # add its value to the money robbed up to the previous house without robbing it If we don't rob the
            # current house, take the maximum of the money robbed up to the previous house with and without robbing it
            curr_robbed = prev_not_robbed + nums[i]
            curr_not_robbed = max(prev_robbed, prev_not_robbed)

            # Update the variables for the next iteration
            prev_robbed = curr_robbed
            prev_not_robbed = curr_not_robbed
            print(prev_not_robbed)
            print(prev_robbed)

        # Return the maximum of the two variables representing the maximum money robbed with and without robbing the
        # last house
        return max(prev_robbed, prev_not_robbed)


# Test the rob function with the provided example
print(Solution.rob([2, 7, 9, 3, 1, 5, 2]))


class Solution:
    @staticmethod
    def rob(nums: List[int]) -> int:
        """
        Dynamic programming, Tabulation
        """
        # Check if the list of houses is empty
        if not nums:
            return 0

        # Get the length of the list of houses
        n = len(nums)

        # Initialize an array to store the maximum money that can be robbed up to each house
        dp = [0 for _ in range(n + 1)]

        # If there's only one house, return the money from that house
        if n == 1:
            return nums[0]

        # If there are only two houses, return the maximum money that can be robbed from either house
        if n == 2:
            return max(nums)

        # Initialize the first two elements of dp array with the money from the first and second houses respectively
        dp[0], dp[1] = nums[0], max(nums[0], nums[1])

        # Iterate over the remaining houses starting from the third house
        for i in range(2, n):
            # Calculate the maximum money that can be robbed up to the current house
            dp[i] = max(dp[i - 2] + nums[i], dp[i - 1])

        # Return the maximum money that can be robbed up to the last house
        return dp[n - 1]
