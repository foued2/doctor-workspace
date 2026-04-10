from typing import List


class Solution:
    @staticmethod
    def numberOfArithmeticSlices(nums: List[int]) -> int:
        """
        Dynamic Programming
        """
        ans = 0
        n = len(nums)

        # Dynamic Programming Approach: Keep track of the arithmetic slice lengths
        dp = [0] * n

        # Iterate through the list starting from the second index
        for i in range(2, n):
            # Check if the i-th element continues the arithmetic sequence
            if nums[i] - nums[i - 1] == nums[i - 1] - nums[i - 2]:
                # Length of arithmetic slice ending at index i is one more than that ending at i-1
                dp[i] = dp[i - 1] + 1
                # Add to the number of arithmetic slices
                ans += dp[i]

        return ans


if __name__ == "__main__":
    print(Solution.numberOfArithmeticSlices([1, 2, 3, 4]))  # Output: 3
    print(Solution.numberOfArithmeticSlices([1]))  # Output: 0
    print(Solution.numberOfArithmeticSlices([1, 2, 5, 7, 8, 9]))  # Output: 1