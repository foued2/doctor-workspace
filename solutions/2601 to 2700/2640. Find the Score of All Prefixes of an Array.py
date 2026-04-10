from typing import List


class Solution:
    @staticmethod
    def findPrefixScore(nums: List[int]) -> List[int]:
        # Get the length of the input list
        n = len(nums)

        # Initialize a list 'dp' to store the prefix scores, starting with zeros
        dp = [0] * n

        # Initialize 'max_nums' to store the maximum number encountered so far, starting with the first element
        max_nums = nums[0]

        # The first element in 'dp' is the sum of the first element in 'nums' and 'max_nums' (which is the same
        # initially)
        dp[0] = nums[0] + max_nums

        # Loop through the list starting from the second element (index 1) to the end
        for i in range(1, n):
            # Update 'max_nums' to be the maximum of the current 'max_nums' and the current element in 'nums'
            max_nums = max(max_nums, nums[i])

            # Calculate the current prefix score as the sum of the previous prefix score,
            # the current element in 'nums', and the updated 'max_nums'
            dp[i] = dp[i - 1] + nums[i] + max_nums

        # Return the list of prefix scores
        return dp


print(Solution.findPrefixScore(nums=[2, 3, 7, 5, 10]))
