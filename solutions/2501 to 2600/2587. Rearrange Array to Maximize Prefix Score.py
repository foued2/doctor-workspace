from typing import List


class Solution:
    @staticmethod
    def maxScore(nums: List[int]) -> int:
        # Initialize the answer variable to keep track of the maximum score
        ans = 0

        # Determine the length of the input list
        n = len(nums)

        # Sort the list in descending order to maximize the sum at each step
        nums = sorted(nums, reverse=True)

        # If the first element (the largest element in the sorted list) is greater than 0,
        # we can consider it as a positive contribution and increment the score
        if nums[0] > 0:
            ans += 1

        # Iterate over the list starting from the second element
        for i in range(1, n):
            # Add the current element to the previous cumulative sum
            nums[i] += nums[i - 1]

            # If the current cumulative sum is greater than 0, increment the score
            if nums[i] > 0:
                ans += 1

        # Return the final calculated score
        return ans


# Test the function with the provided example list
print(Solution.maxScore(nums=[2, -1, 0, 1, -3, 3, -3]))

